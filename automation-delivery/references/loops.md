# Repetição e retomada
Loop simples exige chave estável string, itens independentes, mesma sequência/verificação, retorno conhecido ao início e ausência de variantes/approvals por item. Caso contrário entregar run_one validado e extensão documentada, não prometer lote pronto.

## Limite estável
Helper seleciona items[:limit]. Default 1; reexecução pula o mesmo primeiro item concluído e **não avança ao segundo**. limit>1 exige allow_batch=True e autorização humana prévia para lote real. Testar camada de repetição com dados sintéticos, sem usar produção como teste. Input não pode ser reordenado/reduzido para esconder tentativa anterior.

```python
from pathlib import Path
from checkpoint_runner import Item, VerifiedResult, run_batch

def run_one(item):
    result = process_order(item.payload)  # Implementar com alvos observados.
    return VerifiedResult(verify_order_result(item.key, result))

summary = run_batch(items, run_one, checkpoint=Path('.state/orders.json'),
                    environment='hml-tenant-account', flow_version='v1', limit=1)
```
Copiar helper/testes para módulo do projeto e adaptar imports. Funções ilustrativas precisam implementação real; não retornar True apenas porque não houve exceção.

| Estado | Significado / retomada |
|---|---|
| ausente | Ainda não começou neste checkpoint |
| started | Persistido antes da ação; possível interrupção; reconciliar |
| unknown | Callback falhou/não comprovou; consultar sistema |
| done | Resultado comprovado e checkpoint salvo; pular |
| failed_preflight | Validação local pura falhou antes do callback; retry explícito depois de corrigir |

Preflight não pode clicar, navegar ou enviar pedidos. Toda falha em run_one é conservadoramente incerta. Uma tentativa started/unknown bloqueia novas ações, mesmo fora do prefixo atual. Fechar cookie/modal não prova que salvar falhou. Consultar protocolo/chave e evidência; se concluído marcar done por rotina revisada; se comprovadamente não houve efeito, preparar retomada explícita documentada. Não apagar estado nem usar novo checkpoint para contornar.

## Persistência e concorrência
Checkpoint guarda hashes, estados e hora, não payload. Hashes de IDs previsíveis não são anonimização: .state privado e ignorado. Escopo vincula ambiente/conta/tenant, versão e entrada ordenada. Não colocar credenciais nesses valores.

Temporário no mesmo volume + fsync + substituição atômica; sem promessa de durabilidade contra queda de energia ou transação distribuída. Usar disco local confiável; compartilhar rede exige validação. Lock exclusivo só coordena quem usa o mesmo checkpoint. Não paralelizar sessão; outro checkpoint/máquina não está protegido. Lock órfão exige confirmar processo encerrado e reconciliar antes de remover, sem recuperação por idade/PID isolado.

Não há exactly-once remoto: crash após efeito e antes do done deixa estado incerto bloqueado. Usar idempotência nativa quando documentada e autorizada, mantendo reconciliação.
