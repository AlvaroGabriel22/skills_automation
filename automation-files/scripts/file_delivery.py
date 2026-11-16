#!/usr/bin/env python3
"""Promover arquivo já validado pelo negócio, sem sobrescrever destino."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile

INCOMPLETE = {'.crdownload', '.part', '.tmp'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(path):
    st = path.stat()
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns


def basic_validate(path, kind):
    if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
        raise ValueError('Origem deve ser arquivo regular não vazio')
    if path.suffix.lower() in INCOMPLETE:
        raise ValueError('Download temporário')
    with path.open('rb') as source:
        head = source.read(512).lstrip().lower()
    if head.startswith((b'<!doctype html', b'<html')):
        raise ValueError('HTML inesperado; verificar exportação/sessão')
    if kind == 'pdf' and not head.startswith(b'%pdf-'):
        raise ValueError('Cabeçalho PDF ausente')
    if kind == 'xlsx':
        with zipfile.ZipFile(path) as z:
            if not {'[Content_Types].xml', 'xl/workbook.xml'}.issubset(z.namelist()):
                raise ValueError('Estrutura XLSX ausente')
    # Parsing completo e validação de negócio cabem ao chamador.


def deliver(source, destination, kind='binary', move=False):
    if kind not in {'binary', 'pdf', 'xlsx'}:
        raise ValueError('Formato não suportado')
    source, destination = Path(source).absolute(), Path(destination).absolute()
    for path in (source, destination):
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError('Links simbólicos não aceitos')
    if source.resolve() == destination.resolve():
        raise ValueError('Origem e destino iguais')
    if destination.exists():
        raise FileExistsError('Destino já existe')
    basic_validate(source, kind)
    before, source_hash = fingerprint(source), digest(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.delivery-', suffix='.tmp', dir=destination.parent)
    staging, published = Path(name), False
    try:
        with os.fdopen(fd, 'wb') as out, source.open('rb') as src:
            shutil.copyfileobj(src, out)
            out.flush()
            os.fsync(out.fileno())
        if fingerprint(source) != before or digest(staging) != source_hash:
            raise RuntimeError('Origem mudou ou cópia divergiu')
        # Publicação atômica no-clobber. Se indisponível, preservar origem.
        os.link(staging, destination)
        published = True
        if digest(destination) != source_hash:
            raise RuntimeError('Destino divergiu')
        removed = False
        if move and fingerprint(source) == before and digest(source) == source_hash:
            try:
                source.unlink()
                removed = True
            except OSError:
                pass
        return {'destination': str(destination), 'sha256': source_hash,
                'bytes': destination.stat().st_size, 'source_removed': removed,
                'source_retained': source.exists(), 'business_validation': 'caller_responsibility'}
    except Exception:
        if published:
            raise RuntimeError('Destino publicado; verificação final inconclusiva. Inspecionar antes de repetir.') from None
        raise
    finally:
        staging.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('destination', type=Path)
    p.add_argument('--kind', choices=['binary', 'pdf', 'xlsx'], default='binary')
    p.add_argument('--move', action='store_true')
    args = p.parse_args()
    try:
        result = deliver(args.source, args.destination, args.kind, args.move)
    except Exception as exc:
        print(json.dumps({'status': 'error', 'type': type(exc).__name__,
                          'action': 'Inspecionar origem/destino; não repetir exportação automaticamente'}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
