---
name: automation-web-discovery
description: "Investigar DOM e acessibilidade para automação web. Usar para localizar alvos únicos, iframes aninhados, Shadow DOM, SVG, canvas, grids virtuais e obstáculos como popups, modais e banners de cookies."
---

# Investigar com evidências
Ler [busca guiada](references/guided-search.md), [elementos especiais](references/special-elements.md) quando necessário e [fontes oficiais](references/sources.md) para APIs/versionamento.

1. Confirmar aba, tela, URL sem parâmetros sensíveis, login e item. Enumerar frames pela API permitida; não supor documento principal.
2. Combinar visão visual e DOM/acessibilidade no menor contêiner útil. Ler labels, roles e atributos estáveis, sem valores de senha/cookies ou dumps completos.
3. Restringir por região, formulário, diálogo, linha e chave de negócio. Conferir quantidade, visibilidade e contexto.
4. Preferir role+nome, label, test id contratual, atributos semânticos e CSS curto observado. Evitar XPath absoluto, classes geradas e first/nth usados para ocultar ambiguidade.
5. Distinguir hipótese de alvo observado. Sem candidato único, investigar antes de agir. Não clicar em vários botões até algum funcionar.
6. Registrar seletor, frame chain, contêiner, evidência, estabilidade, pré e pós-condição em docs/targets.json.
7. Devolver alvo à automation-web-execution; acesso à automation-access; controles nativos à automation-sap-desktop.

Inspecionar também o que está **na frente**: modal, backdrop, cookies, spinner, diálogo JS, nova janela e avisos do navegador. Não usar force click, dispatch_event ou remoção do overlay para ocultar o bloqueio. Quando depender do humano, informar onde agir, ação específica, resultado esperado e última etapa confirmada; reobservar antes de retomar.

Usar scripts/dom_inventory.js somente se avaliação DOM for permitida. É leitura limitada de metadados, não uma API de interação. Se proibida, usar inspeção nativa da ferramenta. Labels/IDs também podem conter dados internos. O script não atravessa frames nem Shadow DOM fechado.

Após falha, renovar observação e testar hipótese diferente: frame, diálogo, duplicidade, carregamento, idioma, virtualização ou sessão. Limitar tentativas de investigação, nunca repetir gravações incertas.

Para alterações do helper, executar scripts/test_browser_local.py com Playwright e Chromium compatível. Testes sintéticos não homologam o site do usuário.
