# Busca guiada e obstáculos
Para cada alvo: pergunta → hipótese → evidência mínima → conclusão → ação. Não repetir consulta sem nova informação.

| Ordem | Inspecionar |
|---|---|
| Contexto | Aba, título, usuário/empresa e item |
| Obstáculos | Modal, cookies, overlay, spinner ou desafio |
| Escopo | Região e caminho explícito de frames |
| Semântica | Role, label, nome acessível, atributo estável |
| Acionabilidade | Quantidade, visibilidade, habilitação e sobreposição |
| Resultado | Pós-condição vinculada ao item |

Combinar screenshot e árvore de acessibilidade/DOM. Uma imagem informa posição e sobreposição; DOM informa estrutura. Nenhum sozinho garante o alvo certo. Priorizar role+nome exato, label, test id contratual e CSS curto; restringir por diálogo/linha antes de aumentar complexidade. Não usar classes hash, XPath absoluto ou primeiro botão Salvar.

## O que cobre o alvo
Inspecionar dialog/alertdialog, aria-modal, backdrop, banner, loading, painéis e cabeçalhos sticky; sistemas legados podem não ter roles. z-index alto não basta por causa de contextos de empilhamento e top layer. Se leitura JS for permitida, usar elementsFromPoint no ponto visível do alvo, interpretando descendentes/ícones e Shadow hosts. Verificar também o documento pai do iframe.

`click(trial=True)` pode diagnosticar acionabilidade sem clique, mas pode rolar e interagir com modificadores; não é leitura estritamente sem efeitos. Nunca resolver bloqueio com force=True, dispatch_event, click JS, remover disabled/backdrop ou alterar CSS.

| Superfície | Tratamento |
|---|---|
| Modal DOM | Ler objetivo e agir dentro do diálogo correto |
| alert/confirm/prompt JS | Handler específico antes da ação; só aceitar confirmação prevista |
| Nova página | Associar ao disparo e conferir origem |
| Popup bloqueado pelo navegador | Permissão restrita ao site quando autorizada; humano se necessário |
| Banner cookies | Rejeitar opcionais/necessários quando opção clara |
| Cookies de terceiros | Confirmar mensagem/política; login em loop sozinho não prova causa |
| Certificado, Salvar como nativo | Adaptador específico ou humano |
| Loading | Espera por estado com prazo |
| MFA/CAPTCHA | automation-access, sem contorno |

## Busca avançada e handoff
Buscar código/documentação do sistema antes da web pública. Rede só quando necessário/autorizado: registrar status/tipo/path sanitizado, sem headers, cookies ou bodies. Preferir API documentada se adequada, sem substituir tarefa UI por endpoint interno desconhecido ou burlar controles.

Ao esgotar hipóteses, informar última etapa comprovada, obstáculo, ação humana, onde agir e resultado esperado. Ler recovery.md da skill automation-web-execution resolvida pelo catálogo. Depois do humano, revalidar identidade, item e efeitos persistidos.
