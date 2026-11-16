---
name: automation-files
description: "Atribuir, validar e entregar downloads e exportações web ou SAP. Usar para aguardar conclusão, mover arquivos sem sobrescrever, conferir formatos/conteúdo e preparar entradas de planilhas preservando IDs."
---

# Entregar o arquivo correto
1. Resolver destino no executor real; não supor Downloads em inglês ou unidade Windows em Linux. Verificar escrita, sem sobrescrever arquivos anteriores.
2. Web: expect_download antes do disparo, failure() e save_as antes de fechar contexto; usar staging único. Se o usuário exigir passagem por Downloads, usar subpasta exclusiva ali.
3. Desktop: configurar nome/pasta exclusivos. Em Downloads compartilhado, inventariar antes e atribuir por ação, horário, padrão e chave; não escolher simplesmente o mais recente.
4. Esperar fim de .part/.crdownload/.tmp, estabilidade e parsing. Estabilidade sozinha não prova conclusão; combinar sinal do aplicativo e conteúdo com timeout.
5. Validar formato real, tamanho, cabeçalhos e item/filtros/período. HTML de login com extensão XLSX é falha. Vazio só é aceito conforme contrato.
6. Depois da validação de negócio, usar scripts/file_delivery.py para promoção sem sobrescrever, verificação de hash e remoção posterior da origem se solicitada.

Ler [arquivos e planilhas](references/files.md). O helper não valida regras do relatório. Não executar macros/scripts baixados nem alterar entrada original para status sem pedido; usar checkpoint separado.
