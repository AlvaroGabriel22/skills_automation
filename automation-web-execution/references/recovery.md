# Recuperação e intervenção humana
| Sintoma | Diagnóstico | Recuperação |
|---|---|---|
| Clique interceptado | Modal, backdrop, cookies, layout | Identificar função da camada e tratar pela UI |
| Alvo ausente | Aba/frame/tela/seletor | Nova inspeção, sem inventar fallback |
| Vários candidatos | Escopo insuficiente | Região/diálogo/chave exata |
| Desabilitado | Dependência, permissão, processamento | Ler validação, não remover disabled |
| Spinner persistente | Rede, sessão ou erro | Espera limitada e diagnóstico |
| Popup ausente | Aviso navegador, mesma aba ou falha | Conferir contexto e efeito antes de repetir |
| Login voltou | Expiração, SSO/MFA/cookies | Autenticar e revalidar conta/item/filtros |
| Timeout pós-salvar | Resultado incerto | Consultar chave/protocolo, sem retry cego |
| Arquivo inválido | Exportação incompleta ou login | Conferir conteúdo e estado da exportação |

Retry de leitura pode usar backoff limitado. Não aplicar retry genérico ao redor de run_one nem classificar falha “segura” só por texto de erro.

## Cookies e políticas
Banner: necessários/rejeitar opcionais quando claro. Cookies de terceiros: exigir evidência específica; login em loop também pode ser rede/credenciais. Consultar documentação oficial da versão do navegador e, se permitido, orientar exceção **somente para o site**. Não desabilitar proteção global, TLS ou política corporativa. Se configuração gerenciada, encaminhar domínio/mensagem/etapa ao administrador, sem tokens.

Popup bloqueado: orientar liberação apenas do popup necessário. Conferir se aba já abriu antes de redisparar; ação original pode também ter salvo dados. CAPTCHA/MFA/certificado/política exige intervenção apropriada, nunca bypass.

## Handoff acionável
Persistir docs/resume.md: última etapa confirmada; bloqueio sanitizado; máquina/navegador/aba/janela; controle observado; passos humanos curtos; sinal esperado; efeitos já confirmados ou incertos; próximo passo seguro.

Exemplo: “O aviso de cookies de terceiros está impedindo o login na aba do portal. No navegador executor, use a configuração indicada pelo aviso para autorizar somente este site, se permitido. Se estiver gerenciado, peça liberação ao suporte. Mantenha a aba aberta e avise quando concluir; vou conferir login e item antes de continuar.” Informar se alguma OS foi salva somente com base em evidência.

Não pedir genericamente “resolva”. Sem diagnóstico suficiente, pedir a menor observação útil; não solicitar screenshot se já consegue ver. Após “concluído”, reobservar identidade, empresa/mandante, item, destino, filtros e resultado persistido. Reobter locators após recarga; não reiniciar desde o login ou repetir Salvar cegamente.

Logs devem conter etapa, classe de erro e estado conhecido, sem payload ou erro remoto completo. Capturar região necessária, revisar antes de compartilhar e manter artefatos privados fora do versionamento.
