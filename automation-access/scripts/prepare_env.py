#!/usr/bin/env python3
"""Preparar arquivos locais sem ler/imprimir segredos ou sobrescrever .env."""
import argparse
import json
import os
from pathlib import Path

PROFILES = {
    'web': ['AUTOMATION_BASE_URL', 'AUTOMATION_USER', 'AUTOMATION_PASSWORD', 'AUTOMATION_OUTPUT_DIR'],
    'sap': ['SAP_SYSTEM', 'SAP_CLIENT', 'SAP_USER', 'SAP_PASSWORD', 'SAP_SESSION_ID', 'AUTOMATION_OUTPUT_DIR'],
}
IGNORE = ['.env', '.env.*', '!.env.example', '.auth/', '.state/', 'browser-profile/',
          'artifacts/private/', '*.har', 'trace*.zip', '.venv/', '__pycache__/']


def check_regular(path):
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError('Caminho deve ser arquivo regular')


def create_private(path, content):
    check_regular(path)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as out:
        out.write(content)
        out.flush()
        os.fsync(out.fileno())
    return True


def prepare(project, profile):
    if profile not in PROFILES:
        raise ValueError('Perfil desconhecido')
    project = Path(project).absolute()
    if any(p.is_symlink() for p in [project, *project.parents]):
        raise ValueError('Usar diretório sem links simbólicos')
    project.mkdir(parents=True, exist_ok=True)
    env, example, ignore = (project / n for n in ('.env', '.env.example', '.gitignore'))
    for path in (env, example, ignore):
        check_regular(path)
    previous = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    missing = [rule for rule in IGNORE if rule not in previous.splitlines()]
    if missing:
        with ignore.open('a', encoding='utf-8', newline='\n') as out:
            out.write(('\n' if previous and not previous.endswith('\n') else '') + '\n'.join(missing) + '\n')
    content = '# Preencher localmente; não enviar valores no chat.\n' + ''.join(k+'=\n' for k in PROFILES[profile])
    example_new = create_private(example, content)
    env_new = create_private(env, content)
    return {'project': str(project), 'env_created': env_new, 'example_created': example_new,
            'required_keys_for_profile': PROFILES[profile], 'existing_env_preserved': not env_new,
            'note': 'Arquivo existente não foi lido. Confira Git ignore, rastreamento e ACL Windows.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--profile', choices=PROFILES, default='web')
    args = p.parse_args()
    try:
        result = prepare(args.project, args.profile)
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'error', 'type': type(exc).__name__}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
