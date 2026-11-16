#!/usr/bin/env python3
"""Executar testes incluídos. --browser adiciona cenários sintéticos Playwright."""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    dirs = ['automation-access', 'automation-files', 'automation-delivery', 'automation-sap-desktop']
    failures = []
    for name in dirs:
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s',
                                 str(root/name/'scripts'), '-p', 'test_*.py', '-v'])
        if result.returncode:
            failures.append(name)
    if args.browser:
        result = subprocess.run([sys.executable, str(root/'automation-web-discovery/scripts/test_browser_local.py'), '-v'])
        if result.returncode:
            failures.append('automation-web-discovery')
    print('Resultado: '+('falhou em '+', '.join(failures) if failures else 'todos os testes selecionados passaram'))
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
