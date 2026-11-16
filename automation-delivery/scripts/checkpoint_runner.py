#!/usr/bin/env python3
"""Runner sequencial conservador. Não há exactly-once entre UI remota e disco local."""
import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Mapping


class RunnerError(RuntimeError):
    """Erro sanitizado."""


class BusyCheckpoint(RunnerError):
    pass


class ReconciliationRequired(RunnerError):
    pass


@dataclass(frozen=True)
class Item:
    key: str
    payload: Mapping


@dataclass(frozen=True)
class VerifiedResult:
    verified: bool


def _now():
    return datetime.now(timezone.utc).isoformat()


def _digest(value):
    try:
        encoded = json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError):
        raise RunnerError('Entrada precisa ser JSON válido, sem segredos.') from None
    return hashlib.sha256(encoded).hexdigest()


def _atomic_write(path, data):
    if path.is_symlink():
        raise RunnerError('Checkpoint não pode ser link simbólico.')
    fd, name = tempfile.mkstemp(prefix='.checkpoint-', suffix='.tmp', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, sort_keys=True, indent=2)
            out.write('\n')
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def _exclusive_lock(path):
    lock = path.with_name(path.name + '.lock')
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise BusyCheckpoint('Checkpoint ocupado; verificar processo e estado antes de remover lock.') from None
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump({'pid': os.getpid(), 'created_at': _now()}, out)
            out.flush()
            os.fsync(out.fileno())
        yield
    finally:
        lock.unlink(missing_ok=True)


def _load(path, scope, item_ids):
    if path.is_symlink():
        raise RunnerError('Checkpoint não pode ser link simbólico.')
    if not path.exists():
        return {'version': 1, 'scope': scope, 'items': {}}
    try:
        state = json.loads(path.read_text(encoding='utf-8'))
        if (not isinstance(state, dict) or state.get('version') != 1 or state.get('scope') != scope
                or not isinstance(state.get('items'), dict)):
            raise ValueError
        for key, record in state['items'].items():
            if (key not in item_ids or not isinstance(record, dict)
                    or record.get('status') not in {'started', 'unknown', 'done', 'failed_preflight'}
                    or not isinstance(record.get('updated_at'), str)):
                raise ValueError
    except (OSError, ValueError, TypeError):
        raise RunnerError('Checkpoint inválido ou incompatível com ambiente, fluxo ou entrada.') from None
    return state


def run_batch(items, run_one, *, checkpoint, environment, flow_version, limit=1,
              allow_batch=False, preflight=None, retry_preflight=False):
    """Executar prefixo estável items[:limit]. Preflight deve ser puro/local."""
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or (limit > 1 and not allow_batch):
        raise RunnerError('Limite positivo; acima de 1 exige allow_batch=True.')
    if not isinstance(environment, str) or not environment.strip():
        raise RunnerError('Informe ambiente.')
    if not isinstance(flow_version, str) or not flow_version.strip():
        raise RunnerError('Informe versão do fluxo.')
    snapshot, keys = list(items), set()
    for item in snapshot:
        if (not isinstance(item, Item) or not isinstance(item.key, str) or not item.key.strip()
                or item.key in keys or not isinstance(item.payload, Mapping)):
            raise RunnerError('Itens exigem chaves string únicas e payload de mapeamento.')
        keys.add(item.key)
    scope = _digest({'environment': environment, 'flow': flow_version,
                     'input': [{'key': x.key, 'payload': dict(x.payload)} for x in snapshot]})
    ids = {_digest(x.key) for x in snapshot}
    path = Path(checkpoint).absolute()
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise RunnerError('Checkpoint deve usar diretório sem links simbólicos.')
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = {'completed': 0, 'skipped': 0, 'selected': min(limit, len(snapshot))}
    with _exclusive_lock(path):
        state = _load(path, scope, ids)
        if any(r['status'] in {'started', 'unknown'} for r in state['items'].values()):
            raise ReconciliationRequired('Tentativa incerta; consultar sistema antes de retomar.')
        for item in snapshot[:limit]:
            key = _digest(item.key)
            record = state['items'].get(key)
            if record and record['status'] == 'done':
                summary['skipped'] += 1
                continue
            if record and record['status'] == 'failed_preflight' and not retry_preflight:
                raise RunnerError('Corrigir validação local e usar retry_preflight explicitamente.')
            state['items'][key] = {'status': 'started', 'updated_at': _now()}
            _atomic_write(path, state)
            if preflight is not None:
                try:
                    preflight(item)
                except Exception:
                    state['items'][key] = {'status': 'failed_preflight', 'updated_at': _now()}
                    _atomic_write(path, state)
                    raise RunnerError('Preflight local falhou antes de run_one; sem retry automático.') from None
            try:
                result = run_one(item)
                if not isinstance(result, VerifiedResult) or result.verified is not True:
                    raise ValueError('Não comprovado')
            except Exception:
                state['items'][key] = {'status': 'unknown', 'updated_at': _now()}
                _atomic_write(path, state)
                raise ReconciliationRequired('Resultado incerto; consultar sem repetir ação.') from None
            state['items'][key] = {'status': 'done', 'updated_at': _now()}
            _atomic_write(path, state)
            summary['completed'] += 1
    return summary


def main():
    p = argparse.ArgumentParser(description='Demo sintético; não conecta a sites ou SAP.')
    p.add_argument('--checkpoint', type=Path, required=True)
    p.add_argument('--limit', type=int, default=1)
    p.add_argument('--allow-batch', action='store_true')
    args = p.parse_args()
    demo = [Item('SYNTHETIC-001', {'value': 1}), Item('SYNTHETIC-002', {'value': 2})]
    try:
        report = run_batch(demo, lambda item: VerifiedResult(item.payload['value'] > 0),
                           checkpoint=args.checkpoint, environment='synthetic-local',
                           flow_version='demo-1', limit=args.limit, allow_batch=args.allow_batch)
    except RunnerError as exc:
        p.exit(2, str(exc)+'\n')
    print(json.dumps(report))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
