# Evidência de teste e aceite
| Camada | Comprova | Não comprova |
|---|---|---|
| Estrutura/sintaxe | Frontmatter, links, import e compilação | Resultado de negócio |
| Unitário | Casos dos helpers e invariantes | Interface do usuário |
| Navegador sintético | DOM, frames, overlays, eventos e arquivos da fixture | PLM real, VPN, SSO corporativo |
| Fake SAP | Seleção/limites/inventário de objetos fake | COM Windows, IDs ou autorização SAP |
| Um caso real | Resultado daquele item no ambiente observado | Todas as variantes ou lote |

Antes de execução real, testar preservar IDs/zeros, ambiguidade de alvo/sessão, cookies/modal sobre botão, expiração de sessão e handoff, arquivo inválido/colisão, falha antes/depois de salvar, limite 1 e retomada que não avança silenciosamente. Nenhum teste deve usar credenciais reais por padrão.

Comprovar negócio: registro consultável/protocolo e dados corretos; ou arquivo parseado com filtros/chave corretos no destino. Toast e arquivo não vazio são insuficientes. Se exploração manual já consumiu caso real, não duplicar para testar script: informar limite da validação.

Registrar docs/validation.md com data, comando, versão, ambiente, resultado, falhas e pendências. Não transportar contagens de testes de outra versão como se fossem atuais. Reconstrução de arquivos exige novos testes.

Entrega: run_one implementado; configuração sem segredos; alvos observados; rotina de arquivos; checkpoints quando aplicável; comando unitário; lote simples opcional testado sinteticamente; documentação do contrato e da retomada. Marcar parcial se houver seletores/integrações pendentes. Não chamar pass/TODO/mock de caminho final.
