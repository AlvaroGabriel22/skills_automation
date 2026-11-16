# skills_automation
Skills de automação

Rede de sete skills para orientar um agente de codificação a descobrir, executar e transformar um fluxo web ou SAP desktop em código organizado e verificável. Suporta sites diversos; PLM é um exemplo, não uma dependência específica.

## Começar

Peça ao agente:

> Leia `automation-orchestrator/SKILL.md` deste repositório e use a rede de skills para executar meu fluxo. Descubra e valide somente um item do início ao fim; gere a automação estruturada e testada. Se a repetição for simples, implemente e teste o loop com dados sintéticos, mantendo a execução real limitada a um item.

Complete o pedido com URL ou sistema SAP, tela/transação, campos/valores, resultado esperado e destino. Não inclua senha. Se faltarem credenciais, a rede orienta criar `.env` no projeto da automação e pedir preenchimento local.

Para descoberta automática em um agente que suporte skills, disponibilize as sete pastas no diretório de skills configurado nesse agente. Mantenha cada `SKILL.md` e seus recursos juntos. A rede resolve dependências pelo campo `name`, inclusive quando instaladores renomeiam pastas. Publicar este repositório não instala as skills automaticamente em uma conta ou aplicativo.

## Mapa

| Skill | Responsabilidade |
|---|---|
| [automation-orchestrator](automation-orchestrator/SKILL.md) | Escopo, coordenação, aceite e entrega |
| [automation-web-discovery](automation-web-discovery/SKILL.md) | DOM, acessibilidade, frames, SVG, Shadow DOM, grids e busca guiada |
| [automation-web-execution](automation-web-execution/SKILL.md) | Navegação, campos, eventos, modais e verificação |
| [automation-access](automation-access/SKILL.md) | .env, SSO, MFA, VPN e sessão |
| [automation-sap-desktop](automation-sap-desktop/SKILL.md) | SAP GUI Windows, seleção de sessão, controles e exportação |
| [automation-files](automation-files/SKILL.md) | Atribuição de downloads, parsing e movimentação sem overwrite |
| [automation-delivery](automation-delivery/SKILL.md) | Arquitetura, testes, checkpoints, CLI e loop simples |

## Comportamento esperado

- Fechar um caso completo. Exploração manual e script contam juntos para o limite real de um item.
- Inspecionar alvos reais, inclusive iframes aninhados e controles SVG; não inventar seletores ou usar coordenadas desatualizadas.
- Identificar popups, modais, overlays, loading, banners de cookies e bloqueios de navegador antes de agir.
- Tratar escolhas claras; quando houver bloqueio, informar ao humano onde agir, qual ação executar, como reconhecer conclusão e de onde o agente retomará.
- Reobservar o sistema após intervenção humana e reconciliar resultado incerto antes de repetir uma gravação.
- Manter `run_one(item)` separado do loop. Reexecutar com limite 1 não avança silenciosamente ao segundo item.
- Documentar contrato, alvos, responsabilidades, validação e retomada no projeto gerado.
- Separar validação sintética de homologação no sistema real. Uma skill não concede ferramentas, VPN, permissão ou acesso a desktop.

## Utilitários incluídos

| Arquivo | Uso |
|---|---|
| `automation-access/scripts/prepare_env.py` | Criar configuração vazia e exclusões, preservando `.env` existente |
| `automation-web-discovery/scripts/dom_inventory.js` | Inventariar metadados DOM com limites, sem ler valores dos campos |
| `automation-sap-desktop/scripts/sap_probe.py` | Listar sessões e IDs SAP somente leitura; requer Windows/pywin32 para uso real |
| `automation-files/scripts/file_delivery.py` | Promover arquivo validado sem sobrescrever destino; hash e remoção posterior |
| `automation-delivery/scripts/checkpoint_runner.py` | Runner sequencial com limite, checkpoint e bloqueio de tentativas incertas |

São componentes de apoio: nenhum deles contém um fluxo real de PLM/SAP pronto. O agente deverá implementar os adaptadores a partir dos alvos e regras observados. Parsing de negócio do arquivo continua sendo responsabilidade do projeto gerado.

## Testar

Python 3.10 ou superior. Os 35 testes unitários usam a biblioteca padrão, inclusive fakes SAP; não exigem conta, senha ou acesso externo.

```bash
python scripts/run_tests.py
```

Para adicionar os três cenários locais de navegador, instalar dependências e o Chromium gerenciado pelo Playwright em um ambiente que permita isso:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/run_tests.py --browser
```

Ou usar um navegador compatível já instalado, apontando `AUTOMATION_TEST_BROWSER` para o executável. No Linux, por exemplo:

```bash
AUTOMATION_TEST_BROWSER=/usr/bin/chromium python scripts/run_tests.py --browser
```

Não há ajuste automático de políticas do navegador/SAP. O teste browser abre um contexto descartável com páginas sintéticas; não acessa PLM, SAP ou perfil real. Um erro de inicialização é reportado como falha, não como teste aprovado/ignorado.

O projeto final pode precisar de dependências adicionais conforme a tarefa (python-dotenv, parser de planilha, pywin32 no Windows etc.). Selecionar e fixar as versões efetivamente usadas nesse projeto; não instalar toda dependência possível por antecipação.

## Origem e estado

Esta versão foi **reconstruída em 16/11/2026 a partir do conteúdo registrado na conversa**, porque os arquivos do ambiente anterior ficaram indisponíveis. Mantém os sete domínios e comportamentos combinados, mas não é cópia byte a byte daquela pasta. Os testes foram reconstruídos e executados novamente; não reutilizamos a contagem antiga como prova atual.

Consulte [VALIDATION.md](VALIDATION.md) para comandos, resultados e limitações. SAP real e PLM real não foram homologados. Não há credenciais, estado de login, dados de usuário ou screenshots de conta neste repositório.
