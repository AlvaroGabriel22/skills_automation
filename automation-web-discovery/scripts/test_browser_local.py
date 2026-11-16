#!/usr/bin/env python3
"""Cenários sintéticos locais; requer Playwright e navegador compatível.
AUTOMATION_TEST_BROWSER pode apontar para Chromium/Chrome instalado.
Sem essa variável, usar o Chromium gerenciado pelo Playwright.
"""
import html
import json
import os
from pathlib import Path
import tempfile
import unittest
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeout


class LocalBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = sync_playwright().start()
        options = {'headless': True, 'timeout': 15000}
        if os.environ.get('AUTOMATION_TEST_BROWSER'):
            options['executable_path'] = os.environ['AUTOMATION_TEST_BROWSER']
        try:
            cls.browser = cls.runtime.chromium.launch(**options)
        except Exception:
            cls.runtime.stop()
            raise
        cls.inventory = Path(__file__).with_name('dom_inventory.js').read_text(encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.runtime.stop()

    def setUp(self):
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()
        self.page.set_default_timeout(4000)

    def tearDown(self):
        self.context.close()

    def test_inventory_limits_shadow_overlay_and_no_field_values(self):
        page = self.page
        page.set_content('''<main><input type="password" value="SYNTHETIC_SECRET">
        <button id="export" aria-label="Exportar">Exportar<svg><path d="M0 0"/></svg></button>
        <div id="host"></div><iframe srcdoc="<button id='inner-frame'>Dentro</button>"></iframe>
        <div role="dialog" aria-label="Cookies" id="overlay" style="position:fixed;inset:0;background:white;z-index:10">
        <button>Rejeitar opcionais</button></div></main><div class="duplicate"></div><div class="duplicate"></div>''')
        page.evaluate("document.querySelector('#host').attachShadow({mode:'open'}).innerHTML='<button id=shadow-button>Consultar</button>'")
        before = page.locator('main').inner_html()
        result = page.evaluate(self.inventory, {'rootSelector': 'main', 'probeSelector': '#export'})
        ids = {x['id'] for x in result['candidates']}
        self.assertIn('shadow-button', ids)
        self.assertIn('overlay', ids)
        self.assertNotIn('inner-frame', ids)
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(result))
        self.assertEqual(before, page.locator('main').inner_html())
        self.assertEqual(result['probe']['topToBottom'][0]['id'], 'overlay')
        for selector, expected in [('.duplicate', 'ambiguous_selector'), ('#absent', 'missing_selector'), ('[', 'invalid_selector')]:
            self.assertEqual(page.evaluate(self.inventory, {'rootSelector': selector})['error'], expected)
        bounded = page.evaluate(self.inventory, {'maxNodes': 2})
        self.assertLessEqual(bounded['visited'], 2)
        self.assertTrue(bounded['truncated'])
        bounded = page.evaluate(self.inventory, {'maxCandidates': 1})
        self.assertEqual(len(bounded['candidates']), 1)
        self.assertTrue(bounded['truncated'])

    def test_one_flow_cookies_modal_nested_frames_svg_shadow_download_and_screenshot(self):
        inner = '''<label>Número da OS<input id="order"></label><div id="actions"></div>
        <p role="status" id="status">Aguardando</p>
        <button id="export" aria-label="Exportar relatório" disabled><svg width="20" height="20"><title>Ícone</title><path d="M0 0 L20 20"/></svg></button>
        <script>
        const shadow=document.querySelector('#actions').attachShadow({mode:'open'});
        shadow.innerHTML='<button>Consultar</button>';
        shadow.querySelector('button').onclick=()=>{document.querySelector('#status').textContent='OS '+document.querySelector('#order').value;document.querySelector('#export').disabled=false;};
        document.querySelector('#export').onclick=()=>{
          const a=document.createElement('a');a.download='report.csv';
          a.href=URL.createObjectURL(new Blob(['OS,status\\n'+document.querySelector('#order').value+',ok\\n'],{type:'text/csv'}));
          document.body.append(a);a.click();a.remove();
        };
        </script>'''
        outer = '<iframe title="Pesquisa" srcdoc="' + html.escape(inner, quote=True) + '"></iframe>'
        page = self.page
        page.set_content('''<button id="start">Relatórios</button><input type="password" value="SYNTHETIC_ONLY">
        <section role="dialog" aria-label="Cookies" id="cookies" style="position:fixed;inset:0;background:white;z-index:20">
        <button id="reject">Rejeitar opcionais</button><button>Aceitar todos</button></section>
        <section role="dialog" aria-label="Aviso" id="notice" hidden style="position:fixed;inset:0;background:white;z-index:10">
        <p>Relatório de demonstração</p><button id="continue">Entendi</button></section>
        <iframe title="Relatórios" id="reports" hidden srcdoc="''' + html.escape(outer, quote=True) + '''"></iframe>
        <script>
        document.querySelector('#reject').onclick=()=>{document.querySelector('#cookies').hidden=true;};
        document.querySelector('#start').onclick=()=>{document.querySelector('#notice').hidden=false;};
        document.querySelector('#continue').onclick=()=>{document.querySelector('#notice').hidden=true;document.querySelector('#reports').hidden=false;};
        </script>''')
        start = page.get_by_role('button', name='Relatórios', exact=True)
        with self.assertRaises(PlaywrightTimeout):
            start.click(trial=True, timeout=300)
        expect(page.get_by_role('dialog', name='Aviso', exact=True)).to_be_hidden()
        page.get_by_role('dialog', name='Cookies').get_by_role('button', name='Rejeitar opcionais').click()
        expect(page.get_by_role('dialog', name='Cookies')).to_be_hidden()
        start.click()
        page.get_by_role('dialog', name='Aviso').get_by_role('button', name='Entendi').click()
        report = page.frame_locator('iframe[title="Relatórios"]').frame_locator('iframe[title="Pesquisa"]')
        report.get_by_label('Número da OS').fill('000123')
        report.get_by_role('button', name='Consultar', exact=True).click()
        expect(report.get_by_role('status')).to_have_text('OS 000123')
        with page.expect_download() as pending:
            report.get_by_role('button', name='Exportar relatório', exact=True).click()
        download = pending.value
        self.assertIsNone(download.failure())
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'report.csv'
            download.save_as(path)
            self.assertEqual(path.read_text(), 'OS,status\n000123,ok\n')
            screenshot = Path(d)/'evidence.png'
            page.screenshot(path=screenshot, mask=[page.locator('input[type="password"]')])
            self.assertTrue(screenshot.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))

    def test_expected_javascript_dialog_and_popup(self):
        page = self.page
        page.set_content('''<button id="confirm">Confirmar teste</button><p role="status">Pendente</p>
        <button id="popup">Abrir visualização</button><script>
        document.querySelector('#confirm').onclick=()=>{if(confirm('Confirmar demonstração?'))document.querySelector('[role=status]').textContent='Confirmado';};
        document.querySelector('#popup').onclick=()=>{const w=window.open('about:blank','_blank');w.document.write('<h1>Visualização sintética</h1>');};
        </script>''')
        dialogs = []
        def handle(dialog):
            valid = dialog.type == 'confirm' and dialog.message == 'Confirmar demonstração?'
            dialogs.append(valid)
            dialog.accept() if valid else dialog.dismiss()
        page.once('dialog', handle)
        page.get_by_role('button', name='Confirmar teste').click()
        self.assertEqual(dialogs, [True])
        expect(page.get_by_role('status')).to_have_text('Confirmado')
        with page.expect_popup() as opened:
            page.get_by_role('button', name='Abrir visualização').click()
        popup = opened.value
        expect(popup.get_by_role('heading')).to_have_text('Visualização sintética')
        popup.close()
        self.assertEqual(len(self.context.pages), 1)


if __name__ == '__main__':
    unittest.main()
