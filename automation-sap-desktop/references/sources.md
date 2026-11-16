# Fontes SAP e desktop
Consultar versão do cliente e confirmar APIs na documentação oficial. Exemplos da rede não são IDs reais do usuário.

- SAP GUI Scripting API: https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8
- GuiSession (Busy/Info/FindById): https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8/a4e022f6c155414d9c8ae8eba422cac5.html
- SapGuiAuto/GetScriptingEngine: https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897faf66a6c0885a8/cc21a893b44f435e85daceb2305f1026.html
- Segurança do conector: https://help.sap.com/docs/build-process-automation/sap-build-process-automation/security-aspects-of-sap-gui-connector
- pywinauto, diferenças UIA/Win32: https://github.com/pywinauto/pywinauto/blob/master/docs/getting_started.txt

Scripting precisa estar permitido em cliente/servidor, podendo haver restrições por usuário/readonly. Não alterar parâmetros/RZ11/registro no escopo de uma tarefa comum de automação. SAP GUI Windows COM e GUI Java não são intercambiáveis. Consultar tipos específicos de grids na versão usada, em vez de inferir métodos de outro toolkit.
