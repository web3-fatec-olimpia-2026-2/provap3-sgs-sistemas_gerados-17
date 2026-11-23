# ILP-037 — Laboratório da Aula 03

### Encapsulamento: proteja a capacidade do Quarto

Bem-vindo ao laboratório. Aqui você pratica **encapsulamento** em Python puro, protegendo um atributo com `@property` e `setter`.

## 📂 O que tem aqui

```
lab03/
├── ROTEIRO.md          ← COMECE POR AQUI. O passo a passo.
├── quarto.py           ← a classe que você vai completar
├── tests/
│   └── test_quarto.py  ← os testes (não altere; são o alvo)
├── pytest.ini          ← configuração (deixa o pytest achar o quarto.py)
├── requirements.txt    ← a única dependência: pytest
└── README.md           ← este arquivo
```

## 🚀 Começando (3 comandos)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Depois, **abra o `ROTEIRO.md`** e siga os passos. Rode os testes com:

```bash
python3 -m pytest tests/ -v
```

No começo: **3 verdes, 1 vermelho**. Quando terminar: **4 verdes**.

## ⚠️ Se der `ModuleNotFoundError`

Rode com `python3 -m pytest` (com o `-m`). O `pytest.ini` já resolve o resto.

## 🎫 Uso de IA

Nível 2 — pode usar para destravar, declare trechos acima de 5 linhas, e saiba explicar cada um.

---

*ILP-037 · FATEC Olímpia · 2026/2*
