# Django Study Hub

Aplicação de consulta **estática**, em português, para a disciplina Desenvolvimento Web III. A busca e as preferências são locais; não há backend, login, LLM, API paga ou build. O projeto guiado apresenta 14 passos a partir de uma pasta vazia, com localização, ação, responsabilidade e explicação para cada bloco. A versão da aplicação é uma base inicial curada, **não é uma documentação completa do Django**.

## Materiais analisados

- `Diagrama_Prova_P3_WebIII.pdf`, página 1: oito entregáveis, código no Forms e capturas de HTML, JSON e testes; prova individual, documentação oficial e sem IA.
- `IMPRIMIR_44_Caderno_de_Revisao_WebIII.pdf`, páginas 1–3: foco em ORM e templates; `filter` versus `get`; `clean_campo`; contexto de template; cenário Passeio.
- `[FATEC]-[WEBIII]-Aula14e15-2026.pdf`, páginas 1–26: revisão dos seis conceitos, API e simulado. Os slides agrupam os mesmos assuntos em cinco/seis blocos; o diagrama detalha **oito entregáveis**, ordem adotada aqui. O diagrama pede um ou mais testes passando; o hub oferece três camadas para praticar. A aula informa 120 minutos.
- O caderno simplifica dizendo que validação é do Form. Tecnicamente o Django também oferece validação de model via `full_clean()`, mas `save()` não a chama automaticamente; uma validação implementada somente no Form não protege gravações pelo ORM ou pela API. O problema de contexto divergente é **uma possível causa** de lista vazia, não a única.

Os materiais são usados para identificar exigências da disciplina, não como autoridade técnica. A documentação oficial do Django é a referência técnica para Django (série **5.2 LTS**); os materiais não especificam versão. Os links de cada entrada apontam ao assunto da documentação. Python, DRF e pytest-django são projetos separados e **não são especificados pela documentação Django**. Para não atribuir indevidamente seus comportamentos ao Django, o hub identifica esses trechos e oferece como referência complementar as documentações oficiais próprias. A versão ilustrativa do DRF é 3.16. Verifique a compatibilidade dos pacotes com sua versão de Python. A documentação de Django não valida por si só os exemplos de DRF ou pytest.

**Atenção:** o material recebido estabelece consulta apenas à documentação oficial durante a prova e proíbe IA. Este hub destina-se ao estudo prévio: não se deve presumir que seja permitido usá-lo na avaliação.

## Como executar e publicar

Abra a pasta do projeto com um servidor HTTP estático, por exemplo `npx serve .` ou a extensão Live Server do VS Code; abra o endereço indicado. Não é necessário Python para usar o hub. Apenas abrir `index.html` com `file://` pode bloquear a leitura dos arquivos JSON. É necessária rede para acessar os links externos e para carregar o site inicialmente; não há service worker nem garantia de funcionamento offline após carregamento.

Para publicar no GitHub Pages:

1. Envie o **conteúdo desta pasta** para a raiz de um repositório GitHub (inclusive `index.html`, `src/` e `data/`).
2. Em **Settings → Pages**, selecione **Deploy from a branch**, a branch desejada e a pasta `/ (root)`; salve.
3. Acesse a URL publicada informada pelo GitHub. Os recursos usam caminhos relativos; a navegação usa hash (`#/doc/filter`, por exemplo), permitindo links diretos mesmo em repositórios cujo site tem prefixo no caminho, sem configuração de rewrite do servidor.
4. Depois de modificar JSON ou código, faça commit e push. Não é necessário compilar o site.

Alternativamente, sirva esta pasta em qualquer hospedagem estática. Favoritos, pesquisas, histórico, tema e indicador de assuntos visitados ficam no `localStorage` do navegador, isolados por origem; limpar os dados do navegador os remove. O progresso contabiliza visitas, não aprendizagem concluída. As respostas do simulado não são persistidas nem corrigidas automaticamente.

## Base de conhecimento e manutenção

O exemplo adota **`exemplo/` como raiz**, `exemplo/resort/` como pacote de configuração, `exemplo/quartos/` como app, e `exemplo/quartos/templates/quartos/` para templates. É uma escolha didática, não uma obrigação do Django. A página **Projeto guiado** apresenta a árvore de arquivos e diferencia caminhos físicos, URLs HTML e endpoints. `exemplo/quartos/api.py` reúne serializer e ViewSet; `exemplo/resort/urls.py` registra o router.

- `data/categories.json` lista os módulos; `data/<id-do-módulo>.json` guarda os tópicos e seus códigos, termos e fontes.
- `data/didatica.json` reúne para cada ID os campos `location` (`file`, `folder`, `action`, `responsibility`), `scenario`, `prerequisites`, `breakdown`, `connection`, `expected`, `practice` e, quando aplicável, `lines`.
- `data/prova-p3.json` contém as etapas, e `data/p3-context.json` identifica cada bloco pelo par número/label e registra localização e explicação.
- `data/guia.json` contém o percurso em ordem de dependência, com metadados de localização em cada bloco.

Para adicionar uma entrada, crie um ID único na categoria correspondente e acrescente seu contexto ao `didatica.json`. Para uma categoria nova, adicione-a a `categories.json`, crie seu arquivo JSON e inclua esse nome na lista de carregamento em `src/app.js`. A busca pondera título, palavras-chave, sinônimos, código, descrição e caminho, com correspondência aproximada. Confira sempre os fragmentos, seus requisitos e fontes. `python tests/validate_data.py` valida IDs, relações e metadados; é uma ferramenta **opcional de manutenção**, não uma dependência da aplicação.

Os scripts geradores são uma forma alternativa de manutenção e **sobrescrevem os JSON**. Se optar por alterá-los, mantenha as mudanças neles e regenere nesta ordem:

```bash
python build_data.py
python augment.py
python build_p3.py
python build_guide.py
python build_context.py
python tests/validate_data.py
```

`augment.py` acrescenta a base didática; `build_context.py` adiciona explicações por linha, exercícios e os metadados da P3. O guia e a P3 extraem trechos dos arquivos de `exemplo/`. Alternativamente edite apenas os JSON e não execute os geradores antes de reconciliar as alterações. Atenção: alterações diretas no exemplo só chegam ao guia/P3 ao regenerar seus dados.

## Exemplo completo (opcional, requer Python)

O aplicativo web de consulta **não depende** desse exemplo. Para executar o projeto didático Django/DRF localmente:

```bash
cd exemplo
python -m venv .venv
# Ative o ambiente: Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# em outro terminal, com o ambiente ativo:
pytest -v
```

Visite `/quartos/`, `/quartos/novo/` e `/api/quartos/`. O projeto de exemplo inclui migração inicial. Para testar o admin, execute `python manage.py createsuperuser` e acesse `/admin/`. `settings.py` usa chave e `DEBUG` para ambiente local: **não é configuração de produção**. A regra customizada do `QuartoForm` só se aplica a esse form; proteja igualmente as demais entradas antes de uma aplicação real. A API de exemplo também não configura autenticação/autorização de produção.

## Verificação

Foram validados o parsing e a integridade dos JSON, a sintaxe JavaScript e a renderização dos 46 tópicos, das oito etapas e do guia em ambiente DOM automatizado. A busca foi testada com as 23 frases de intenção do enunciado. O guia e a sequência P3 foram montados, a partir dos próprios trechos, em projetos Django novos: as migrações, três testes (`pytest`), cadastro e listagem HTML e requisições GET/POST da API passaram. O layout possui breakpoints para desktop e celular, mas o teste automatizado de DOM não substitui a inspeção visual em dispositivos reais. O funcionamento pode variar conforme navegador e permissões de clipboard/localStorage.
