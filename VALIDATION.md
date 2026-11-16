# Validação da reconstrução — 16/11/2026

Esta evidência pertence ao conteúdo reconstruído neste repositório. Não comprova equivalência byte a byte com a pasta anterior nem homologação de um sistema do usuário.

| Verificação | Resultado |
|---|---|
| `.env`: criação, preservação, exclusões e symlink | 3 testes aprovados |
| Arquivos: cópia/movimento, colisão, inválido, estrutura XLSX, publicação não suportada | 5 testes aprovados |
| Runner: limite estável, retomada, escopo, lock, crash e falha após efeito | 15 testes aprovados |
| SAP fake: seleção inequívoca, identidade, Busy, limites e leitura de metadados | 12 testes aprovados |
| Total unitário | **35 testes aprovados** |
| Python compileall e node --check do inventário DOM | Aprovados |
| Sete skills: frontmatter, metadados e links locais | Aprovados |
| Navegador sintético | **Bloqueado na inicialização; 0 testes executados** |
| PLM real / SAP Windows real | Não executados |

## Comandos usados

```bash
python -m unittest discover -s automation-access/scripts -p 'test_*.py' -v
python -m unittest discover -s automation-files/scripts -p 'test_*.py' -v
python -m unittest discover -s automation-delivery/scripts -p 'test_*.py' -v
python -m unittest discover -s automation-sap-desktop/scripts -p 'test_*.py' -v
python -m compileall -q .
node --check automation-web-discovery/scripts/dom_inventory.js
AUTOMATION_TEST_BROWSER=/usr/bin/chromium python automation-web-discovery/scripts/test_browser_local.py -v
```

Validação estrutural adicional: `quick_validate.py` do criador de skills disponível no ambiente, mais resolução de todos os links locais Markdown e conferência do prompt em `agents/openai.yaml`.

## Ambiente e bloqueio do navegador

Linux, Python 3.12, Playwright 1.62.0 e PyYAML 6.0.3. Chromium foi encerrado antes de criar página: `socket() failed: Operation not permitted` durante inicialização de process_singleton. Não foi alterada a política do ambiente para contornar o bloqueio. Os testes browser continuam executáveis, mas não são contados entre os 35 aprovados.

Os três cenários incluídos são: inventário limitado/open Shadow DOM/overlay/ausência de valores; fluxo cookies→modal→frames aninhados→SVG/Shadow DOM→download→screenshot mascarada; diálogo JavaScript esperado e nova aba. É necessário executá-los em ambiente compatível antes de afirmar validação funcional desta reconstrução no navegador.

## Limites dos helpers

- Cabeçalho/estrutura e hash não substituem parsing e validação de negócio.
- O runner bloqueia incerteza; não oferece exactly-once com um sistema remoto nem recuperação automática de lock órfão.
- Timeout SAP é verificado entre chamadas COM; uma chamada bloqueada pode excedê-lo.
- Fakes SAP não validam Windows, COM, permissões, IDs reais ou uma transação.
- Diretórios de trabalho devem ser controlados. Filesystems de rede e concorrência por caminhos diferentes exigem validação específica.
