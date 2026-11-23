"""
Hotel Resort — COMMAND (GoF · comportamental): cada AÇÃO vira um objeto (dá para desfazer e refazer).

ANTES (nucleo/antes_comandos.py): alterar_antigo(item, campo, valor) muda o objeto direto — não
sobra registro do valor anterior, então não há como desfazer.
DEPOIS (aqui):
  * AlterarCampo guarda O QUE fazer (campo, valor novo) e lembra o valor ANTIGO para desfazer;
  * Historico (o INVOCADOR) executa comandos e os empilha: desfazer() e refazer() em ordem;
  * a Reserva (o RECEPTOR) não sabe nada de histórico — os setters continuam validando.
Quando NÃO usar: ação simples que nunca será desfeita, enfileirada ou registrada.
"""


class Comando:
    """Interface: todo comando sabe executar e desfazer."""

    def executar(self):
        raise NotImplementedError

    def desfazer(self):
        raise NotImplementedError


class AlterarCampo(Comando):
    """Comando CONCRETO: troca um campo da Reserva e lembra o valor anterior."""

    def __init__(self, item, campo, valor):
        self.item = item
        self.campo = campo
        self.valor = valor
        self.anterior = None

    def executar(self):
        self.anterior = getattr(self.item, self.campo)
        setattr(self.item, self.campo, self.valor)  # o setter valida (pode levantar ValueError)

    def desfazer(self):
        setattr(self.item, self.campo, self.anterior)

    def __repr__(self):
        return f"AlterarCampo({self.campo}={self.valor!r})"


class Historico:
    """INVOCADOR: executa, empilha e desfaz/refaz comandos."""

    def __init__(self):
        self._feitos = []
        self._desfeitos = []

    def executar(self, comando):
        comando.executar()  # se falhar (ValueError), nada entra no histórico
        self._feitos.append(comando)
        self._desfeitos.clear()  # ação nova apaga o que dava para refazer

    def desfazer(self):
        if not self._feitos:
            return False
        comando = self._feitos.pop()
        comando.desfazer()
        self._desfeitos.append(comando)
        return True

    def refazer(self):
        if not self._desfeitos:
            return False
        comando = self._desfeitos.pop()
        comando.executar()
        self._feitos.append(comando)
        return True

    def acoes(self):
        return [repr(comando) for comando in self._feitos]
