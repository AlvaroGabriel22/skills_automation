#!/usr/bin/env python3
"""Inventário SAP Windows somente leitura. COM pode bloquear além do prazo de polling."""
import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import sys
import time
from typing import Any


class ProbeError(RuntimeError):
    """Erro operacional sanitizado."""


@dataclass
class SessionRecord:
    session: Any = field(repr=False)
    session_id: str
    busy: bool | None
    system: str | None = None
    client: str | None = None
    user: str | None = field(default=None, repr=False)
    number: int | None = None
    issue: str | None = None

    def public(self):
        return {'session_id': self.session_id, 'busy': self.busy, 'system': self.system,
                'client': self.client, 'session_number': self.number, 'issue': self.issue}


def short(value):
    return str(value)[:200]


def check_deadline(deadline):
    if time.monotonic() >= deadline:
        raise ProbeError('Prazo excedido entre chamadas COM.')


def iter_collection(collection, cap, deadline):
    check_deadline(deadline)
    try:
        count = int(collection.Count)
    except Exception:
        raise ProbeError('Não foi possível ler coleção SAP.') from None
    if count < 0 or count > cap:
        raise ProbeError('Coleção excede limite; restrinja escopo.')
    for index in range(count):
        check_deadline(deadline)
        try:
            child = collection(index)
        except Exception:
            raise ProbeError('Coleção SAP mudou ou está inacessível.') from None
        yield child


def list_sessions(engine, deadline, cap=100):
    records = []
    try:
        connections = engine.Children
    except Exception:
        raise ProbeError('Scripting Engine indisponível.') from None
    for connection in iter_collection(connections, cap, deadline):
        try:
            sessions = connection.Children
        except Exception:
            raise ProbeError('Conexão não permite enumerar sessões.') from None
        for session in iter_collection(sessions, cap, deadline):
            if len(records) >= cap:
                raise ProbeError('Limite total de sessões excedido.')
            check_deadline(deadline)
            try:
                record = SessionRecord(session, short(session.Id), bool(session.Busy))
            except Exception:
                raise ProbeError('Sessão inacessível ou fechada.') from None
            if record.busy:
                record.issue = 'busy: aguarde e repita a listagem'
            else:
                try:
                    info = session.Info
                    record.system, record.client, record.user = str(info.SystemName), str(info.Client), str(info.User)
                    record.number = int(info.SessionNumber)
                except Exception:
                    record.issue = 'identidade indisponível'
            records.append(record)
    return records


def select_session(records, system, client, user, session_id=None):
    if not all((system, client, user)):
        raise ProbeError('Informe sistema, mandante e usuário.')
    relevant = [r for r in records if session_id is None or r.session_id == session_id]
    if any(r.issue or r.busy is not False for r in relevant):
        raise ProbeError('Sessão ocupada/inacessível no escopo; aguarde ou refine por ID.')
    matches = [r for r in relevant if (r.system, r.client, r.user) == (system, client, user)]
    if len(matches) != 1:
        raise ProbeError('Nenhuma sessão corresponde.' if not matches else 'Sessão ambígua; informe ID exato.')
    return matches[0]


def wait_ready(session, deadline, interval=0.1):
    while True:
        check_deadline(deadline)
        try:
            busy = bool(session.Busy)
        except Exception:
            raise ProbeError('Não foi possível consultar Busy.') from None
        check_deadline(deadline)
        if not busy:
            return
        time.sleep(min(interval, max(0, deadline-time.monotonic())))


def assert_identity(record):
    try:
        info = record.session.Info
        current = (str(info.SystemName), str(info.Client), str(info.User),
                   str(record.session.Id), int(info.SessionNumber))
    except Exception:
        raise ProbeError('Não foi possível reconfirmar identidade.') from None
    if current != (record.system, record.client, record.user, record.session_id, record.number):
        raise ProbeError('Sessão mudou; inspecionar novamente.')


def inventory(session, deadline, max_nodes=300, max_depth=8):
    if max_nodes < 1 or max_depth < 0:
        raise ProbeError('Limites inválidos.')
    pending, result = [(session, 0)], []
    truncated, unreadable = False, 0
    while pending:
        if len(result) >= max_nodes:
            truncated = True
            break
        check_deadline(deadline)
        node, depth = pending.pop()
        try:
            item = {'id': short(node.Id), 'type': short(node.Type), 'name': short(node.Name), 'depth': depth}
        except Exception:
            unreadable += 1
            continue
        result.append(item)
        try:
            is_container = bool(node.ContainerType)
        except Exception:
            item['children_unreadable'] = True
            unreadable += 1
            continue
        if not is_container:
            continue
        if depth >= max_depth:
            item['depth_limit'] = True
            truncated = True
            continue
        try:
            children = node.Children
            count = int(children.Count)
            if count < 0:
                raise ValueError
            available = max_nodes - len(result) - len(pending)
            chosen = min(count, max(0, available))
            if chosen < count:
                truncated = True
            for index in range(chosen-1, -1, -1):
                check_deadline(deadline)
                pending.append((children(index), depth+1))
        except ProbeError:
            raise
        except Exception:
            item['children_unreadable'] = True
            unreadable += 1
    return {'components': result, 'truncated': truncated, 'unreadable': unreadable}


def positive(value):
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError('deve ser positivo')
    return n


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group()
    modes.add_argument('--list', action='store_true')
    modes.add_argument('--inventory', action='store_true')
    for key in ['system', 'client', 'user', 'session-id']:
        p.add_argument('--'+key)
    p.add_argument('--max-nodes', type=positive, default=300)
    p.add_argument('--max-depth', type=positive, default=8)
    p.add_argument('--timeout', type=positive, default=15)
    p.add_argument('--output', type=Path)
    args = p.parse_args(argv)
    if args.inventory and not all((args.system, args.client, args.user)):
        print('Informe sistema, mandante e usuário.', file=sys.stderr)
        return 2
    if os.name != 'nt':
        print('Probe real requer Windows com SAP GUI e pywin32.', file=sys.stderr)
        return 2
    try:
        import pythoncom
        import win32com.client
    except ImportError:
        print('pywin32 não disponível neste Python.', file=sys.stderr)
        return 2
    initialized = False
    try:
        pythoncom.CoInitialize()
        initialized = True
        app = win32com.client.GetObject('SAPGUI').GetScriptingEngine
        deadline = time.monotonic()+args.timeout
        records = list_sessions(app, deadline)
        result = {'sessions': [r.public() for r in records]}
        if args.inventory:
            record = select_session(records, args.system, args.client, args.user, args.session_id)
            wait_ready(record.session, deadline)
            assert_identity(record)
            result['inventory'] = inventory(record.session, deadline, args.max_nodes, args.max_depth)
        if args.output:
            fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as out:
                json.dump(result, out, ensure_ascii=False, indent=2)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ProbeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception:
        print('Falha de acesso/COM/saída; conferir sessão e política sem alterar SAP.', file=sys.stderr)
        return 2
    finally:
        if initialized:
            pythoncom.CoUninitialize()


if __name__ == '__main__':
    raise SystemExit(main())
