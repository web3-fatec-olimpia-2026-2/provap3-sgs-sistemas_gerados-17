"""
Confere as suas consultas. Escreva cada consulta no arquivo minhas_consultas.py
(nas variaveis CONSULTA_1, CONSULTA_2, ...) e rode: python3 verificar.py
Verde = acertou. Vermelho = tente de novo (a dica aparece).
"""
import sqlite3, sys

try:
    import minhas_consultas as m
except ImportError:
    print("ERRO: crie o arquivo minhas_consultas.py (copie de exemplo_consultas.py)")
    sys.exit(1)

con = sqlite3.connect("resort.db")
cur = con.cursor()

def roda(sql):
    try:
        return [tuple(r) for r in cur.execute(sql)]
    except Exception as e:
        return f"ERRO SQL: {e}"

testes = [
    ("CONSULTA_1", "Todos os quartos: numero e diaria",
     sorted([(101,200.0),(102,200.0),(201,500.0),(301,1200.0)])),
    ("CONSULTA_2", "So quartos com diaria acima de 300",
     sorted([(201,500.0),(301,1200.0)])),
    ("CONSULTA_3", "Quantas reservas existem no total (uma linha, um numero)",
     [(5,)]),
    ("CONSULTA_4", "Nome do hospede e numero do quarto de cada reserva (JOIN)",
     sorted([("Ana Souza",101),("Bruno Lima",201),("Carla Dias",101),
             ("Diego Melo",301),("Ana Souza",201)])),
]

acertos = 0
for var, desc, esperado in testes:
    sql = getattr(m, var, None)
    print(f"\n{var}: {desc}")
    if not sql or not sql.strip():
        print("  [ ] vazio - ainda nao respondida")
        continue
    got = roda(sql)
    if isinstance(got, str):
        print(f"  [X] {got}")
        continue
    if sorted(got) == esperado:
        print("  [OK] verde!")
        acertos += 1
    else:
        print(f"  [X] resultado diferente do esperado.")
        print(f"      voce trouxe {len(got)} linha(s); esperado {len(esperado)}.")

con.close()
print(f"\n=== {acertos} de {len(testes)} consultas corretas ===")
