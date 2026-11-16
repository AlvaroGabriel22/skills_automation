# Contrato compartilhado
Definir antes de efeitos de negócio. Reusar autorização já dada; pedir somente decisões ou recursos ausentes.

## docs/flow.md
Registrar objetivo verificável; ambiente/SO/versões; sistema/URL sem query sensível; operação (consultar/exportar/criar/atualizar); primeiro item; limite real 1 compartilhado entre exploração e script; entrada (origem, abas, colunas, filtros, tipos, vazios); saída (estado/protocolo/arquivo/destino); autenticação sem segredo; efeitos autorizados; fora do escopo; aceite; variantes não testadas.

## docs/targets.json
```json
{"schema_version":1,"targets":[{"logical_name":"export_report","surface":"web","page":"report","frame_chain":[],"scope":"report toolbar","strategy":"role+accessible_name","selector":null,"evidence":"not_observed","unique":null,"precondition":"filters checked","postcondition":"download attributed and parsed"}]}
```
`null` é pendência, não seletor funcional. Preencher somente após observar. Para SAP acrescentar sistema/mandante/sessão/control_id; para UIA janela/automation_id/control_type. Registrar idioma/versão e instabilidade relevante.

## Diário privado
Guardar em artifacts/private/, ignorado pelo versionamento: run_id, chave opaca, etapa, hora, estado e referência da evidência. Estados conceituais: planned, started, verified, uncertain, blocked. Persistir started antes de qualquer ação que possa mudar negócio. Crash/timeout após envio permanece incerto até consulta independente. Não persistir payload completo, senha, cookie ou token. O runner usa nomes started/unknown/done/failed_preflight documentados em sua referência.

## docs/validation.md
Registrar comando, data, ambiente, resultado e limite da evidência. Distinguir primeira execução real observada, testes locais e reprodução real pelo script. Excluir evidências sensíveis do pacote.

## docs/resume.md
```text
Status: blocked / awaiting_human
Etapa e última pós-condição confirmada:
Bloqueio observado (mensagem sanitizada e tipo de superfície):
Onde agir (máquina, aplicativo, aba/janela, tela e controle):
Ação humana necessária (passos específicos e curtos):
Por que não executei (falta de ferramenta, decisão ou política):
Sinal esperado para retomar:
Efeitos já executados (nenhum, confirmado, incerto):
Próximo passo seguro (consultar antes de repetir gravação):
Captura local, se disponível e apropriada:
```
Exemplo: “A janela Confirmar acesso está cobrindo Exportar. Na aba PLM, conclua a verificação e mantenha a tela Relatórios aberta. Avise quando terminar; conferirei os filtros antes de exportar.” Não dizer apenas “faça manualmente”. A confirmação humana não substitui reobservação da tela.
