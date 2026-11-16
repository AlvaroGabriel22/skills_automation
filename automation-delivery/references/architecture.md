# Responsabilidades e projeto
Definir entrada, saída, pré-condição, efeito e pós-condição antes de abstrair. run_one(item) é unidade de trabalho; leitura de planilha e repetição não conhecem seletores.

| Módulo | Responsabilidade |
|---|---|
| config.py | Ambiente, caminhos, timeouts e validação sem segredos nos logs |
| models.py | Item normalizado, resultado e erros |
| flows/process_one.py | Sequência de negócio e comprovação de um caso |
| adapters/web/ | Page objects, frames e alvos observados |
| adapters/sap/ | Seleção de sessão, screen objects, IDs e status |
| services/files.py | Formato/conteúdo e promoção do arquivo |
| services/input.py | CSV/Excel preservando IDs |
| services/checkpoints.py | Limites e retomada, nunca reenvio cego |
| cli.py | Argumentos, modo unitário/lote, saída resumida |
| tests/ | Fixtures e testes sem credenciais por padrão |
| docs/ | Contrato, alvos, validação e handoff sanitizados |

Criar somente módulos necessários; não adicionar plataforma, filas ou banco sem necessidade. Fluxo pequeno pode usar poucos arquivos. Nomear pelo domínio (ReportPage/OrderSearchScreen). Adaptadores expõem intenções como apply_filters e export_report; negócio decide quais OS. Não criar abstração universal web/SAP se apenas um usado. Se híbrido, manter adaptadores separados e compartilhar modelos/arquivos.

Centralizar IDs/seletores e anotar contexto, origem observada e pós-condição. Reobter após mudanças. Logs estruturados run_id/etapa/status, códigos locais AUTH_REQUIRED, TARGET_AMBIGUOUS, BLOCKER_REQUIRES_USER, DOWNLOAD_INVALID, RESULT_UNKNOWN; não payload, query, senha, headers ou erro remoto bruto.

.env apenas para valores locais; cofre existente quando apropriado. CLI unitária e lote explícito. Definir dry-run com ações exatas, sem chamar “seco” um modo que clica até salvar. Fixar versões realmente testadas e dependências usadas; import COM restrito ao adaptador Windows. Entregar README operacional do projeto gerado, .env.example, testes e docs adaptados do modelo, sem placeholders no caminho alegado pronto.
