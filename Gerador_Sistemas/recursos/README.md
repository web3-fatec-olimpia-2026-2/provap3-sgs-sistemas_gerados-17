# Recursos copiados para os sistemas gerados

## Bootstrap 5.3.3 (`bootstrap-5.3.3/`)

| Arquivo | Origem | SRI (sha384) |
|---|---|---|
| `bootstrap.min.css` | https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css | `sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH` |
| `bootstrap.bundle.min.js` | https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js | `sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz` |
| `LICENSE` | https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/LICENSE | — (licença MIT) |

Baixados em 22/11/2026. Os hashes conferem com os oficiais da versão 5.3.3.

**Por que uma cópia local, e não CDN?** As Instruções de desenvolvimento Django (§11.4) pedem
Bootstrap por CDN com versão fixa e SRI. Aqui ele vai **dentro** de cada sistema gerado
(`static/<app>/vendor/bootstrap/`), como foi pedido para o SGS. As vantagens: funciona sem internet
(inclusive no PWA offline) e a CSP fica só com `'self'`, sem abrir exceção para host de terceiros (§14.6).
Para trocar de versão, substitua os arquivos e atualize esta tabela.
