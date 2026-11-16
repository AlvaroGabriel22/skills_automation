# Sessões e diagnóstico
## Credenciais no executor correto
Preparar .env vazio com o helper antes de pedir preenchimento. Preservar arquivos existentes; não abrir/imprimir segredos para “conferir”. Validar só presença de chaves:
```python
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(project_root)/'.env', override=False)
required = ('AUTOMATION_USER','AUTOMATION_PASSWORD')
missing = [k for k in required if not os.environ.get(k)]
if missing:
    raise RuntimeError('Preencha no .env: '+', '.join(missing))
```
Usar cofre corporativo já configurado quando apropriado; não migrar segredos sem necessidade. Não colocar senha em CLI, logs, payload de item ou repr. Windows exige ACL apropriada: chmod não equivale à ACL.

Verificar `git check-ignore --no-index .env` e `git ls-files --error-unmatch .env` sem imprimir conteúdo. .gitignore não remove arquivo rastreado e regras posteriores podem anular exclusões. Preservar arquivo local ao corrigir rastreamento. Se segredo já estiver no histórico, informar necessidade de rotação sem reexibir valor.

## SSO e MFA
Popup de identidade não é anúncio. Manter sessão acessível durante confirmação humana; depois verificar retorno ao aplicativo e conta/empresa. Não coletar OTP no chat/log nem fingir handoff em executor invisível. SSO Windows pode exigir perfil/certificado corporativo que navegador novo não herda; não copiar perfil inteiro nem desabilitar proteções.

## Storage state
Playwright storage_state pode conter cookies/tokens suficientes para impersonar a conta; salvar somente se necessário em .auth/ privado. Confirmar versão e suporte a IndexedDB. SessionStorage não é persistido automaticamente por esse mecanismo. Reautenticar quando expirar e reconstruir apenas estado comprovado, sem despejar cookies para diagnóstico.

## Cookies, rede e autorização
| Sintoma | Próximo teste |
|---|---|
| DNS/host inacessível | URL, VPN e executor na rede correta |
| Certificado inválido | Hostname/cadeia com TI, sem ignore_https_errors indiscriminado |
| 401/login | Sessão/conta e uma tentativa controlada |
| 403 | Permissão do usuário, sem alternar contas por conta própria |
| Loop SSO | Popup bloqueado, cookies, horário/política; não concluir causa sem evidência |
| Senha inválida | Pausar e corrigir localmente, sem retries até bloqueio |
| SAP | Sistema/mandante corretos; preferir SSO |

Bloqueio de cookies de terceiros é diferente de banner. Orientar exceção específica quando permitida; configuração gerenciada requer administrador. Retornar handoff com onde agir, ação, efeito anterior e condição de retomada. Continuar código/testes independentes.

Fontes: https://playwright.dev/python/docs/auth e notas de segurança SAP listadas na skill SAP. Conferir versão quando mudar mecanismo.
