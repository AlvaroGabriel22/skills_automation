---
name: automation-sap-desktop
description: "Investigar e automatizar SAP GUI nativo, inicialmente Windows com Scripting e pywin32. Usar para sessões, transações, ALV, controles, exportações e diálogos Windows; distinguir SAP Fiori/WebGUI, Java e Citrix/RDP."
---

# Automatizar SAP pela superfície correta
1. Classificar Fiori/WebGUI → skills web; GUI Windows → COM Scripting; GUI Java/Linux → API própria a investigar; Citrix/RDP → localizar a máquina que hospeda o SAP.
2. Confirmar Windows interativo, cliente aberto e Scripting permitido no cliente/servidor. Não alterar RZ11, registro ou política por conta própria. Documentar requisito para administração se bloqueado.
3. Preferir SSO/sessão existente; usar automation-access para credenciais.
4. Escolher **uma sessão única** por sistema, mandante e usuário, refinando por ID quando preciso. Nunca assumir Children(0). Preservar outras sessões e trabalho aberto.
5. Inspecionar Id, Type, Name e disponibilidade sem valores desnecessários. Gravação autorizada de scripts pode fornecer IDs, mas requer sanitização e revalidação.
6. Esperar Busy=False; localizar com findById, agir e verificar tela/transação/status. Reobter controles após navegação. E/A são erro, W/I precisam de interpretação; S isolado não prova negócio.
7. Ler [controles](references/controls.md), [implementação](references/implementation.md) e [fontes](references/sources.md).
8. Fechar um item. Sem Windows/SAP, declarar que testes fake não validam COM nem sistema real.

scripts/sap_probe.py enumera sessões e inventaria metadados, sem login, transação ou gravação. Priorizar Scripting → UIA/Win32 → atalhos observados → visão/OCR ancorados. Se só houver pixels, registrar DPI, resolução, foco e verificar cada resultado. Playwright não inspeciona DOM de SAP GUI desktop.

Distinguir wnd[1] SAP de diálogo nativo e notificações Scripting. Classificar modal antes de fechar. Se depender do humano, fornecer janela, controle, ação, sinal de conclusão e ponto de retomada sem duplicar efeito anterior.
