# Arquivos e entradas
## Download atribuído
Registrar listener antes do clique, verificar failure e salvar antes de fechar contexto. Usar staging controlado e exclusivo, não confiar em suggested_filename como caminho. Se popup dispara download, escutar essa página; se PDF inline ou geração assíncrona, observar controles reais. Não forjar endpoints internos para contornar interface.

Desktop: configurar pasta/nome únicos no diálogo. Em pasta compartilhada, inventário anterior + horário + padrão/chave + evento. Múltiplos candidatos exigem diagnóstico, nunca “mais recente”. Esperar fim de sufixos temporários, tamanho estável e parsing; estabilidade sozinha não garante conclusão. Antivirus/rede podem atrasar liberação; usar timeout e preservar arquivo.

## Validar conteúdo
| Formato | Verificação |
|---|---|
| CSV | Encoding/separador, cabeçalhos, colunas, chave/linhas; IDs como string |
| XLSX | ZIP e estrutura; parser como openpyxl para abas/células/chave; fórmulas dependem de cache |
| XLS antigo | Inspecionar binário/HTML real antes de escolher parser; renomear não converte |
| PDF | Cabeçalho + parser, páginas e conteúdo esperado |
| ZIP | Inventário/tamanho e proteção de paths ao extrair; não executar conteúdo |

O helper só valida integridade básica/hash, não filtros, conteúdo de negócio ou PDF completo. HTML disfarçado é erro. Relatório vazio precisa contrato que permita e evidência de zero resultados.

## Promoção sem sobrescrever
Validar negócio primeiro. Recusar destino existente, origem=destino e symlinks. Copiar para temporário no filesystem do destino, fsync e hash; publicar por operação no-clobber (hard link no helper). Se filesystem não suporta, falhar preservando origem em vez de degradar para overwrite. Remover origem só depois de publicação verificada. Se remoção falhar, retornar destino pronto/origem mantida; não refazer exportação.

Helper pressupõe diretórios controlados, não oferece defesa absoluta contra adversário alterando paths em paralelo. Em SMB/compartilhamentos, validar semântica link/lock/rename; não garantir durabilidade contra queda de energia. Conflito exige nome configurado ou decisão humana, não apagar destino existente.

## Planilhas
Inspecionar abas, cabeçalhos, mesclas, vazios, filtros, tipos e fórmulas. Preservar OS 000123 como texto. data_only lê cache, não recalcula; número formatado com zeros pode exigir regra explícita de reconstrução. Selecionar primeiro item válido, deduplicar por chave e manter input original intacto. Checkpoint separado não deve conter payload completo.

Fontes: https://playwright.dev/python/docs/downloads ; https://playwright.dev/python/docs/api/class-download
