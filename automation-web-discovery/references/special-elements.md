# Elementos e superfícies especiais
## Iframes
Enumerar frames por API permitida; registrar nome/origem sem query/token. Criar um nível explícito por iframe observado:
```python
workspace = page.frame_locator('iframe[title="Área de trabalho"]')
report = workspace.frame_locator('iframe[title="Relatório"]')
field = report.get_by_label('Número da OS', exact=True)
```
Nomes são ilustrativos. Cross-origin não é acessível via JS comum do pai; usar API de frames sem desabilitar segurança. Esperar tela interna, reobter contexto após detach/reload e não combinar locators de frames diferentes em has. Modal no pai pode cobrir todo iframe. O inventário JS não entra em frames: executá-lo no contexto correto quando permitido.

## Shadow DOM
Playwright atravessa raízes abertas por locators; XPath não atravessa e raízes fechadas não são suportadas por essa rota. Investigar host e acessibilidade quando fechado; não interceptar attachShadow para modificar o aplicativo. Ausência no inventário não prova ausência visual.

## SVG
SVG inline participa do DOM. Buscar primeiro botão/link com nome acessível que contém o ícone; path frequentemente só desenha. Se SVG for controle, inspecionar role, aria-label, title, grupos e atributos. CSS seleciona SVG; XPath legado pode exigir local-name(), sem justificar caminho frágil. use referencia desenho, não necessariamente alvo do evento. SVG em img não expõe DOM interno; object/embed pode ser outro documento/origem.

## Canvas/visão
Canvas não tem nó por objeto desenhado. Procurar controles acessíveis ou API documentada autorizada. Se só pixels, usar captura recente, âncora visual, DPI/zoom/resolução/janela e conferir resultado a cada ação. Não reutilizar coordenadas após scroll/resize/modal nem dizer que OCR fornece seletor DOM.

## Grids e widgets
Restringir linha pela chave exata; em virtualização, linhas ausentes podem não existir no DOM e índices são reciclados. Preferir filtro do próprio sistema; paginação exige limite, detecção de fim e deduplicação. Conferir filtros antigos, empresa, unidade, período e estado de carregamento antes de concluir “OS ausente”.

Combobox customizado pode renderizar listbox em portal fora do formulário. Abrir, localizar a lista ativa, selecionar e confirmar valor. Datepicker exige formato/localidade, mês/ano e dia correto entre células repetidas. Dropdown nativo usa select_option.

## Inventário limitado
```python
from pathlib import Path
inventory = page.evaluate(
    Path(skill_dir, 'scripts/dom_inventory.js').read_text(encoding='utf-8'),
    {'rootSelector':'main','maxNodes':300,'maxCandidates':60}
)
```
Só usar quando a ferramenta permite JS. O helper retorna metadados, caminhos de shadow aberto, retângulos e heurísticas. Não lê value, textContent, HTML, cookies, storage, não rola/clica/altera DOM. Atributos podem conter dados internos. Não calcula nome acessível completo. Root/probe ausente ou ambíguo é erro. Probe no centro é pista de sobreposição, não prova de clique. Conferir truncated e limites; diagnóstico parcial nunca deve ser tratado como árvore completa.
