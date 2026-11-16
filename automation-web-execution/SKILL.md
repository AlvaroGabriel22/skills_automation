---
name: automation-web-execution
description: "Executar e codificar um fluxo web observado com Playwright. Usar para navegar, preencher, selecionar, tratar abas, diálogos, modais, esperas, exportações e verificar resultados sem duplicar gravações."
---

# Executar por estados observáveis
Preferir Python + Playwright sync em projeto novo, salvo stack/requisito diferente; não misturar sync/async. Adaptar exemplos às APIs permitidas do navegador conectado.

1. Consumir contrato e alvos observados. Não inventar seletores a partir do exemplo do usuário.
2. Conferir pré-condição; usar locators reavaliados em vez de handles duradouros.
3. Aplicar fill/select_option/check/uncheck/press/click conforme controle. Combobox customizado exige abrir a lista correta, selecionar e confirmar valor.
4. Registrar listener antes de popup/download/dialog. Manter referência explícita de cada página.
5. Esperar estado relevante: heading, campo, resposta ou resultado. Evitar networkidle genérico em aplicações com polling e sleeps fixos como espera principal.
6. Registrar tentativa antes de salvar e conferir persistência depois. Timeout pós-envio exige reconciliação, não reenvio.
7. Usar automation-files para arquivos e automation-delivery para consolidar.

Ler [receitas](references/recipes.md) e [recuperação](references/recovery.md). Classificar overlays antes de repetir cliques. Preferir necessários/rejeitar opcionais em cookies quando a escolha for clara; não tratar confirmação de negócio como anúncio. Criar handoff específico em docs/resume.md quando depender do humano.

Clique/toast isolado não prova sucesso. Conferir item, filtros e resultado; não repetir gravação para conseguir screenshot melhor.
