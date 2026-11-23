"""
Cria a pasta treino/ com um repositorio Git pronto para o exercicio de conflito.
Rode UMA vez: python3 preparar.py  ->  depois: cd treino
"""
import subprocess, os, shutil

if os.path.exists("treino"):
    shutil.rmtree("treino")
os.makedirs("treino")
os.chdir("treino")

def git(*args):
    subprocess.run(["git", *args], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

git("init", "-b", "main")
git("config", "user.email", "aluno@fatec.local")
git("config", "user.name", "Aluno")

with open("categorias.txt", "w") as f:
    f.write("categorias do resort:\n- comum\n- [A DEFINIR]\n")

git("add", "categorias.txt")
git("commit", "-m", "cria lista de categorias")

print("Pasta treino/ criada com repositorio Git pronto.")
print("Agora rode:  cd treino")
print("E siga o ROTEIRO.md a partir do Passo 1.")
