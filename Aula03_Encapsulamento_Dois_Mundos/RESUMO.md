# Aula 03 — Consolidar fazendo: encapsulamento em dois mundos

> ILP-037 · 21/08/2026
> Fontes: `ILP037_Aula03_Slides.pdf`, `ILP037_Aula03_LAB_ROTEIRO.md`, laboratório
> (`material_original/ILP037_Laboratorio_Aula03/`), homeworks 03a/b/c (Dropbox), soluções do
> professor (Dropbox) e `complementar_dropbox/encapsulamento-dois-mundos.pdf` + áudios/vídeo.

## 1. Ferramentas (bloco 1)
Teams (material/entregas) · GitHub (código da equipe, cada aula uma branch) · Taiga (quadro da sprint).
Três disciplinas, um produto: **AGO-021** julga o processo, **Web III** o funcionamento,
**ILP-037** a decisão de design.

## 2. Encapsulamento na mão (laboratório)
Classe `Quarto` já protegia `diaria` (`< 0` → erro). Tarefa: proteger `capacidade` com a regra
**mínimo 1** (`< 1` → erro). **A estrutura é a mesma; a regra vem do negócio.**
Desafio: `receita_maxima = diaria × capacidade` (property calculada, sem setter).

Fluxo de teste: `python3 -m pytest tests/ -v` (com `-m`; o `pytest.ini` com `pythonpath = .`
evita `ModuleNotFoundError`). Começa 3 verdes + 1 vermelho (`DID NOT RAISE`) → termina 4 verdes.

## 3. O mesmo conceito, dois mundos ⭐ (cai na prova)

| | Python puro | Django model |
|---|---|---|
| Proteger valor | `@property` + setter | `validators=[MinValueValidator(0)]` no campo (ou `clean()`) |
| Por quê | é a ferramenta da linguagem | o campo alimenta **ModelForm, admin e ORM** |
| `@property` serve para | ler e proteger atributo | **só dado calculado** (ex.: `total`) |
| Setter no campo | — | **quebra** formulário, admin e filtros do ORM |
| Pegadinha | — | `save()` **não valida**; o validador roda via ModelForm/`full_clean()` |

> "A solução certa depende do terreno. Padrão não é receita cega — é decisão."

## 4. Porta para herança
- **É-UM → herança:** `class Suite(Quarto)` + `super().__init__(...)` reaproveita o construtor
  (e as validações) do pai; a suíte só acrescenta `tem_sala`.
- **TEM-UM → composição:** `self.frigobar = Frigobar()` — um objeto contém outro.
- Teste do ouvido: "a suíte é um quarto" ✔ herança; "o quarto é um frigobar" ✘ → composição.

## 5. Atividades

| Atividade | Resolução |
|---|---|
| Laboratório (capacidade + desafio) | `resolucao/lab/quarto.py`, `resolucao/lab/tests/test_quarto.py` (4 originais + 8 meus) |
| Extra: herança/composição | `Suite` e `QuartoComFrigobar` em `resolucao/lab/quarto.py` |
| HW 03a — segunda property | `resolucao/homework/hw03a_segunda_property.py` + teste |
| HW 03b — dois mundos (IA vedada) | `resolucao/homework/hw03b_dois_mundos.md` (modelo de estudo) |
| HW 03c — ADR validação (equipe) | `resolucao/homework/ADR-003-onde-mora-a-validacao.md` |

## 6. Para a prova
- Por que a capacidade usa `< 1` e a diária `< 0`.
- Por que **não** pôr `@property` com setter num campo de model Django.
- `super().__init__` — o que reaproveita.
