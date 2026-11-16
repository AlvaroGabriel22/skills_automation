# Adaptador SAP e limites
Executar Python/pywin32 no Windows que hospeda SAP, em desktop interativo. Linux/WSL não oferece automaticamente COM da sessão Windows. Java tem API própria; Fiori/WebGUI usam web. Citrix/RDP pode mostrar só pixels; preferir agente autorizado no host, verificar DPI/foco e não prometer estabilidade com sessão bloqueada/desconectada sem teste.

## Probe somente leitura
```powershell
python scripts/sap_probe.py --list
python scripts/sap_probe.py --inventory --system QAS --client 100 --user USUARIO --session-id /app/con[1]/ses[2] --timeout 15
```
Valores ilustrativos. ID vem de listagem observada, nunca default zero. Usuário é identificador interno, não senha; saída omite username. --output cria arquivo novo sem sobrescrever. Probe não faz login, navega, abre conexão ou salva; anexar ao SAP pode disparar notificação de Scripting legítima.

Inventário limitado lê Id/Type/Name, não Text/células/valores. Para compreender modal, observar texto mínimo em etapa separada. Limites de tempo são verificados entre chamadas COM: chamada bloqueada pode exceder prazo. Se deadline firme for necessário, processo filho com timeout externo, encerrando só probe, nunca SAP. Interrupção de ação com efeito exige reconciliação.

## Organização
Selecionador de sessão → screen objects → run_one(item) → serviço de arquivos → CLI. Inicializar COM na thread que usa os objetos; não compartilhar sessão entre threads/processos. Reconfirmar identidade antes de agir, pois usuário pode trocar/fechar sessão.

Sequência: confirmar identidade → Busy=False → resolver modal conhecido → pré-condição → checkpoint started → salvar uma vez → esperar → consultar resultado → marcar done. Qualquer dúvida entre salvar e marcar done é incerta, não falha retryable.

## Testes
Fakes Linux provam seleção/limites/erros, não COM/IDs/transação. Windows/SAP: primeiro probe readonly, depois um caso sintético em homologação, depois único caso real autorizado. Exploração e script contam juntos. Registrar versões Python/pywin32/cliente e camadas efetivamente testadas.

Executar `python -m unittest discover -s scripts -p test_sap_probe.py -v` da pasta da skill. Não alterar políticas server/client para testar.
