# Decisões e recuperação
| Evidência | Próxima investigação/ação | Critério de saída |
|---|---|---|
| Alvo não encontrado | Aba, frame, região, idioma, virtualização | Alvo observado e único |
| Clique interceptado | Pilha visual, modal, backdrop, loading | Camada resolvida pela UI |
| Banner de cookies | Necessários/rejeitar opcionais quando claro | Banner fechado e tarefa acessível |
| Bloqueio de cookies de terceiros | Mensagem/política do navegador | Exceção específica autorizada ou login suportado |
| Modal desconhecido | Título, conteúdo e botões | Decisão no escopo ou handoff |
| Timeout depois de Salvar | Consulta por chave/protocolo | Resultado reconciliado, sem retry cego |
| Sessão expirada | Pausar efeitos e autenticar | Conta, item e filtros conferidos |
| Scripting SAP indisponível | Requisito cliente/servidor/admin | Habilitação autorizada ou alternativa suportada |
| Download ausente | Popup, PDF inline, modal, geração assíncrona | Arquivo atribuído à ação |
| Ferramenta indisponível | Código/testes independentes e handoff | Acesso real disponibilizado |

Usar por padrão até três hipóteses diferentes por obstáculo e timeout ajustado ao sistema. Isso não autoriza três cliques em Salvar. Parar antes se houver risco de duplicação, política ou decisão fora do escopo. Registrar esperado/observado/hipótese/evidência/próximo teste. Não tomar silêncio como login concluído.

## Pesquisa guiada
Buscar primeiro em código e documentação disponíveis com rg: label, rota, módulo, test id, mensagem sanitizada. Depois consultar documentação oficial da tecnologia/versão. Exemplos: `site:playwright.dev/python/docs frame locator strict`, `site:help.sap.com GuiGridView GetCellValue`. Remover host interno, pessoa, OS, tokens e dados confidenciais de consultas públicas. Fontes descrevem APIs, não provam IDs do sistema do usuário. Testar hipótese com experimento mínimo e reversível; registrar decisão e referência.

Casos representativos: PLM login→relatório→filtro→exportação→parsing→destino; planilha→um item→consulta/criação autorizada→comprovação→run_one→loop sintético; SAP→sessão única→transação→controle→resultado; modal/cookie→classificação→tratamento/humano→reobservação→retomada.
