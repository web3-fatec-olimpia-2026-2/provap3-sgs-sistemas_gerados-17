# 6 variações de tom por tema (do Claro ao Escuro)

Aplicamos as **6 variações de tom** (`Claro`, `Tom 2`, `Tom 3`, `Tom 4`, `Tom 5` e `Escuro`) nos 10 temas da extensão, corrigimos o **T09 Acessível** nos dois últimos tons para manter o matiz azul e criamos a página HTML interativa com os 10 temas × 6 tons.

---

## 1. Tela de Configurações com o seletor de 6 tons

Em **Configurações → Aparência → Tema**, o seletor de **Variação de tom** oferece os 6 degraus (`Claro`, `Tom 2`, `Tom 3`, `Tom 4`, `Tom 5`, `Escuro`), com `Tom 3` como padrão e as 4 amostras de cor (`Fundos`, `Destaques`, `Escritas` e `Barras`):

![Tela de Configurações com os 6 tons](C:/Users/Usuario/.gemini/antigravity/brain/da84586a-2d4b-438f-b101-865c6ea62704/config-6-tons-tom3.png)

---

## 2. Catálogo completo: 10 temas × 6 tons (60 combinações)

- **T01 a T05 (`Claro`, `Tom 2`, `Tom 3`, `Tom 4`, `Tom 5`, `Escuro`):**

![Temas T01 a T05 nos 6 tons](C:/Users/Usuario/.gemini/antigravity/brain/da84586a-2d4b-438f-b101-865c6ea62704/tons-6-T01-T05.png)

- **T06 a T10 Personalizado (incluindo a correção do T09 Acessível em `Tom 5` e `Escuro` e o controle ao vivo do T10):**

![Temas T06 a T10 nos 6 tons](C:/Users/Usuario/.gemini/antigravity/brain/da84586a-2d4b-438f-b101-865c6ea62704/tons-6-T06-T10.png)

---

## 3. Resumo das alterações aplicadas

| Item | O que foi feito |
| :--- | :--- |
| **Correção do T09 Acessível (`Tom 5` e `Escuro`)** | O destaque escuro de `T09` em [theme.js](file:///z:/home/oscar/projetos/django/whatscrm/extension/lib/theme.js) passou de `#FFD700` (amarelo/oliva) para `#4DA3FF` (azul alto contraste, `7,54:1` sobre `#0A0A0A`), preservando a identidade azul-cobalto/marinho nos 6 tons e mantendo o contraste WCAG AAA (`≥ 7:1` para escrita). |
| **6 variações de tom por tema** | `ESQUEMAS = ['claro', 'tom2', 'tom3', 'tom4', 'tom5', 'escuro']` (`Claro`, `Tom 2`, `Tom 3`, `Tom 4`, `Tom 5`, `Escuro`), com migração automática de `'suave'` legado para `'tom3'`. |
| **T10 Personalizado em 6 tons** | `extremos('T10', cores)` deriva automaticamente os extremos claro e escuro a partir das cores escolhidas (`Fundos`, `Destaques`, `Escritas` e `Barras`) e gera as 6 variações de tom com contraste validado. |
| **Auditoria WCAG e testes** | **0 falhas** em 780 verificações (10 temas × 6 tons) e **30/30 testes automatizados** passando em [theme.test.js](file:///z:/home/oscar/projetos/django/whatscrm/extension/tests/theme.test.js) e [store.test.js](file:///z:/home/oscar/projetos/django/whatscrm/extension/tests/store.test.js). |
| **Página HTML com os 6 tons** | [tons-temas.html](file:///z:/home/oscar/projetos/django/whatscrm/dev/tons-temas.html) e versão autocontida [tons-temas-autocontido.html](file:///z:/home/oscar/projetos/django/whatscrm/dev/tons-temas-autocontido.html) (abre direto com dois cliques). |
