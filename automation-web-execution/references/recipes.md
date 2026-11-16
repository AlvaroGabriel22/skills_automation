# Receitas observáveis
Exemplos ilustrativos Python sync; substituir somente por alvos inspecionados. Usar `from playwright.sync_api import expect`.

## Consultar um item
```python
form = page.get_by_role('region', name='Consulta de OS', exact=True)
field = form.get_by_label('Número da OS', exact=True)
expect(field).to_be_editable()
field.fill(item.os_number)
expect(field).to_have_value(item.os_number)
form.get_by_role('button', name='Consultar', exact=True).click()
row = page.get_by_role('row').filter(has=page.get_by_role('cell', name=item.os_number, exact=True))
expect(row).to_have_count(1)
expect(row).to_be_visible()
```
No iframe, criar todos os locators nesse frame. Zero resultados exige mensagem final e filtros verificados, não timeout traduzido como “não encontrado”. Validar máscaras/formatos após fill. Para upload, usar set_input_files no input observado; não tentar digitar no file chooser do SO sem necessidade.

## Modal DOM
Classificar aviso dispensável, seleção obrigatória, confirmação prevista ou bloqueio. Restringir botões ao diálogo. Exemplo de aviso conhecido sem efeito de negócio:
```python
notice = page.get_by_role('dialog', name='Aviso de manutenção', exact=True)
expect(notice).to_be_visible()
notice.get_by_role('button', name='Fechar', exact=True).click()
expect(notice).to_be_hidden()
expect(page.get_by_role('heading', name='Consulta de OS')).to_be_visible()
```
Escape pode descartar formulário. Não fechar todo modal automaticamente nem instalar handler global que aceite OK. Se voltar, investigar causa com orçamento de tentativas.

## Diálogo JavaScript previsto
Handler que só observa deixa diálogo bloqueado. Instalar antes do disparo; aceitar somente tipo/mensagem previstos, rejeitar inesperado e interromper para reconciliação:
```python
events = []
def handle_dialog(dialog):
    expected = dialog.type == 'confirm' and dialog.message == expected_message
    events.append(expected)
    dialog.accept() if expected else dialog.dismiss()
page.once('dialog', handle_dialog)
try:
    action_button.click()
finally:
    page.remove_listener('dialog', handle_dialog)
if events != [True]:
    raise RuntimeError('Confirmação ausente/inesperada; reconciliar antes de continuar')
```
Não registrar mensagem sensível. Prompt exige valor autorizado; beforeunload exige preservar trabalho. Aceitar dialog não prova persistência.

## Popup
```python
with page.expect_popup() as opened:
    page.get_by_role('link', name='Abrir relatório', exact=True).click()
report_page = opened.value
expect(report_page.get_by_role('heading', name='Relatório')).to_be_visible()
```
Conferir origem antes de inserir dados. Sem evento, investigar bloqueio/mesma aba/falha sem clicar repetidamente. Fechar apenas aba criada pela automação, após concluir.

## Cookies
Ler opções reais. Rejeitar opcionais ou necessários quando claro; preferências podem permitir desativar opcionais e salvar. Não presumir que “Continuar” significa rejeitar nem aceitar todos como fallback. Se única alternativa exigir consentimento amplo, pedir decisão. Não apagar cookies existentes para tentar novamente: isso pode encerrar sessão. Banner do site e política de cookies de terceiros são problemas diferentes.

## Download
```python
with page.expect_download() as started:
    export_button.click()
download = started.value
if download.failure() is not None:
    raise RuntimeError('Download falhou; preservar estado')
download.save_as(staging_file)
```
Aguardar na página que efetivamente dispara. PDF inline/geração assíncrona pode exigir outro passo. Usar automation-files para conteúdo/destino.

## Screenshot
```python
from pathlib import Path
folder = Path('artifacts/private')
folder.mkdir(parents=True, exist_ok=True)
page.screenshot(path=folder/'blocked-step.png', full_page=False,
                mask=[page.locator('input[type="password"]'), observed_personal_data_region])
```
A região mascarada deve ser locator observado. Sem máscara confiável, usar recorte sem dados ou resumo textual. Não alterar CSS para esconder bloqueio. Máscara não protege trace/HAR/vídeo/DOM; não iniciar trace no login nem anexar evidências internas automaticamente. Usar captura suportada em navegador conectado.
