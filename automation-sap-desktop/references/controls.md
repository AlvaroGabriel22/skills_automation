# Controles SAP, modais e exportação
## Seleção e estado
Não confundir sessão ativa visualmente com sessão de trabalho autorizada. Identificar sistema/mandante/usuário e, se houver várias, ID exato. Confirmar transação/tela atual antes de navegar, pois /n pode descartar trabalho. Não fechar sessões de terceiros. Busy=False não prova tela correta; verificar janela ativa, modal e controle esperado.

Obter IDs por árvore Scripting ou gravação autorizada; não adivinhar IDs de screenshots. Guardar Id/Type/Name para estrutura; ler texto mínimo somente quando necessário para compreender erro/modal. Reobter controles após roundtrip.

## Tipos
| Tipo | Abordagem |
|---|---|
| GuiTextField/GuiCTextField | text observado, confirmar valor e validação/Enter quando exigido |
| GuiPasswordField | valor só no login, sem coleta/log |
| GuiButton | press observado, depois pós-condição |
| GuiCheckBox | selected conforme estado desejado, sem toggle cego |
| GuiComboBox | selecionar chave observada, não índice presumido |
| GuiTab | select e reobter filhos |
| GuiTree | chave de nó observada, expandir com limite |
| GuiGridView (ALV) | coluna técnica observada + chave de negócio; GetCellValue/linhas conforme API |
| GuiTableControl (dynpro) | linhas visíveis/scroll, índices podem mudar; conferir chave após rolagem |
| GuiShell | investigar subtipo, não presumir ALV |

Uma linha fora do viewport pode não estar disponível, e ordenar/filtrar muda índices. Preferir busca/filtro do sistema, não loop infinito em coordenadas. Verificar mandante, empresa, período e filtros persistentes.

## Status e modais
Ler MessageType/texto mínimo da status bar quando necessário: E/A bloqueiam; W precisa interpretar, não Enter automático; I pode exigir confirmação; S é apenas evidência auxiliar. Verificar protocolo/registro persistido ou arquivo correto.

wnd[1] pode ser modal SAP (ajuda F4, confirmação, formato, caminho). Salvar como do Windows pode estar fora da árvore SAP: usar pywinauto UIA/Win32 após inspecionar com ferramenta apropriada. Não supor que toda janela é wnd[1] nem que sempre é um aviso fechável.

Classificar título, botões e consequência. Só dispensar aviso sem efeito quando claro. Não pressionar OK globalmente, fechar modal desconhecido ou desabilitar notificações de Scripting para avançar. Se humano necessário: identificar janela, controle, ação e sinal; manter resultado de gravação anterior incerto até consulta.

## Exportação
Observar comando/formato/diálogo reais; não assumir IDs de menu comuns. Preferir staging único, nome determinístico por execução e evitar sobrescrita. No diálogo conferir caminho completo. Aguardar conclusão e validar conteúdo com automation-files; status SAP não garante arquivo pronto. No Citrix, caminho do servidor difere do dispositivo local: confirmar onde o arquivo será salvo.
