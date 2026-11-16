---
name: automation-delivery
description: "Transformar fluxo web ou SAP observado em código Python modular, documentado e testável. Usar para arquitetura, CLI, testes, checkpoints e loop simples com limite de um item e retomada sem duplicação."
---

# Entregar automação reproduzível
Ler [arquitetura](references/architecture.md), [testes](references/testing.md) e [loops](references/loops.md); adaptar assets/project_contract.md ao projeto.

1. Reusar arquitetura existente; separar configuração, negócio, adaptadores, arquivos e CLI. Manter run_one(item) independente da planilha.
2. Centralizar seletores/IDs observados em page/screen objects; definir pós-condições e timeouts.
3. Criar .env.example, exclusões, dependências usadas e comando reproduzível. Registrar versões efetivamente testadas, sem inventar lockfile.
4. Usar scripts/checkpoint_runner.py como base opcional sequencial: limite 1, opção explícita de lote e bloqueio de resultado incerto. Não envolver run_one em retry genérico.
5. Testar acesso expirado, ambiguidade, frames, arquivo inválido, colisão, falha após salvar e retomada em fixtures.
6. Exploração manual e script contam juntos para um caso real. Se já consumido, não repetir gravação só para justificar “testado”.
7. Entregar caminho validado sem placeholders, comandos e limites explícitos; marcar partes sem acesso como pendentes.

Loop simples exige itens independentes, sequência uniforme, entrada inequívoca, resultado por item, retorno ao início conhecido e ausência de variantes não descobertas. Não paralelizar sessão compartilhada. Se complexo, entregar núcleo unitário e extensão documentada.

Distinguir testes estáticos, unitários, navegador sintético, fake SAP e execução real no docs/validation.md. Ausência de exceção não prova sucesso de negócio.
