# 🧪 Roteiro de Laboratório 1 — MVVM
### ILP-037 · Aula 08 · Resort de Olímpia · Python puro · ~30 min

> **Objetivo:** tirar a decisão de *como mostrar* de dentro da tela e colocá-la numa camada
> **ViewModel**, que prepara o dado pronto para exibição — testável sem renderizar.
>
> **Pacote do aluno:** `ILP037_Laboratorio_Aula08_Lab1_MVVM.zip`
> **Solução do professor (não distribuir):** `SOLUCAO_PROFESSOR_Aula08_Lab1_MVVM.py`

---

## Antes de começar

**🖥️ terminal** — descompacte e entre na pasta:
```
unzip ILP037_Laboratorio_Aula08_Lab1_MVVM.zip
cd ILP037_Lab1_MVVM
python3 -m pytest -v
```

**Resultado esperado:** 8 testes, **todos vermelhos (FAILED)**. É assim mesmo. As classes
`QuartoViewModel` e `PainelQuartosVM` estão vazias. Nosso trabalho é preenchê-las.

> Se aparecer `ModuleNotFoundError`, confira que você está **dentro** de `ILP037_Lab1_MVVM`
> (onde está o `pytest.ini`). O `pytest.ini` já resolve o caminho — não precisa de `PYTHONPATH`.

---

## O "antes" — o cheiro que vamos combater

**📝 VS Code** — abra `quartos.py`. Olhe a função `tela_quartos()`: dentro do laço ela decide
o texto do status, o rótulo do botão, formata o preço e ainda calcula o rodapé "LOTADO". A
decisão de **como mostrar** está presa no **desenho da tela**. Não dá para testar a decisão sem
ler a string. É isso que vamos desgrudar.

---

## Passo 1 — Preencher o `QuartoViewModel` (prepara UM quarto)

**📝 VS Code** — em `quartos.py`, complete o `__init__` do `QuartoViewModel`:

```python
class QuartoViewModel:
    def __init__(self, quarto):
        self.numero = quarto["numero"]
        self.categoria = quarto["categoria"]
        self.disponivel = not quarto["ocupado"]
        self.status_label = "livre" if self.disponivel else "INDISPONIVEL"
        self.botao_label = "Reservar" if self.disponivel else "(ocupado)"
        self.preco_formatado = f"R$ {quarto['diaria']:.2f}"
```

**🖥️ terminal** — rode só os testes do ViewModel de um quarto:
```
python3 -m pytest -v -k "quarto or preco or numero"
```
**Resultado esperado:** os 4 testes de `QuartoViewModel` passam (verdes). Os de painel ainda
falham — é o próximo passo.

> **Leia um verde:** `test_quarto_ocupado_nao_fica_disponivel` passou. Repare: ele perguntou
> `vm.disponivel`, `vm.status_label`, `vm.botao_label` — **direto no ViewModel**, sem desenhar
> tela nenhuma. Essa é a vitória do MVVM.

---

## Passo 2 — Preencher o `PainelQuartosVM` (prepara o PAINEL)

**📝 VS Code** — complete o `__init__` do `PainelQuartosVM`:

```python
class PainelQuartosVM:
    def __init__(self, quartos):
        self.itens = [QuartoViewModel(q) for q in quartos]
        self.livres = sum(1 for i in self.itens if i.disponivel)
        if self.livres:
            self.rodape = f"{self.livres} quarto(s) livre(s)"
        else:
            self.rodape = "LOTADO - nenhum quarto livre"
```

**🖥️ terminal** — rode tudo:
```
python3 -m pytest -v
```
**Resultado esperado:** **8 verdes**. 

> Note que `livres` e o texto do rodapé agora são do **painel**, não da tela. O teste
> `test_painel_sem_vaga_mostra_lotado` confere o "LOTADO" sem procurar a palavra numa string de
> tela — ele lê `painel.rodape`.

---

## Passo 3 — A View fica burra (o "depois")

Agora que o ViewModel prepara tudo, a tela só lê. Veja no arquivo da solução como fica a
`tela_quartos_mvvm()`: um laço que só costura `i.status_label`, `i.botao_label`,
`i.preco_formatado`. **Zero `if` de decisão na tela.** Compare com o `tela_quartos()` original —
todo o "if de aparência" sumiu de lá.

**Prova de que nada quebrou:** a saída de texto final continua a mesma. Mudou **onde** a decisão
mora, não **o que** aparece na tela.

---

## ✅ Pronto quando...
- [ ] `python3 -m pytest` mostra **8 passed**
- [ ] nenhum teste seu procura texto dentro da string da tela
- [ ] você consegue explicar, em uma frase, por que `status_label` está no ViewModel e não na tela

---

## Delimitação em Python (o freio)

- **No servidor (Python/Django):** não há *data binding*. O ViewModel é só uma **classe/função
  de preparação** — monta o dicionário pronto e entrega ao template. Não crie "observables".
- **No navegador (Alpine.js):** aí sim há binding reativo (`x-model`) — é o MVVM clássico, e é o
  que a segunda-feira de vocês tocou.
- **Quando NÃO usar:** se a tela mostra o dado como ele é (sem rótulo condicional, sem
  formatação, sem estado derivado), não há o que preparar. ViewModel aí é cerimônia.

*Fonte da delimitação: GIRIDHAR, Aprendendo Padrões de Projeto em Python.*
