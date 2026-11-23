# Laboratório 1 — MVVM: a camada que prepara os dados para a tela
### ILP-037 · Aula 08 · Resort de Olímpia

## O que tem aqui
- `quartos.py` — o painel de quartos com um **cheiro** (a tela decide regra de negócio) e as classes `QuartoViewModel` / `PainelQuartosVM` **vazias**, que você vai preencher.
- `tests/test_painel.py` — os testes. Agora eles estão **vermelhos**.
- `pytest.ini` — já configurado (resolve o `ModuleNotFoundError`).

## Como rodar
No terminal (🖥️), dentro da pasta do laboratório:

```
python3 -m pytest -v
```

Você verá **8 testes falhando**. É o esperado: as classes estão vazias.

## Sua missão
Mover a **regra** (quarto ocupado não reserva, contar livres) e a
**apresentação** (texto do status, rótulo do botão, "R$", "LOTADO") para
dentro do **ViewModel**. Quando o ViewModel preparar os dados prontos, os 8
testes passam — **sem nenhum teste precisar ler o texto da tela**.

> Dica: você **não** mexe na função `tela_quartos()` do cheiro. Você constrói
> a camada ao lado. No fim, a tela só lê o que o ViewModel preparou.

Prazo e entrega: veja o `HOMEWORK_08`.
