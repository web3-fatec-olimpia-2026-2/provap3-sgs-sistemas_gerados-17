"""
ViagemCerta — FACTORY METHOD (GoF · criação): quem decide QUAL canal criar é a SUBCLASSE.

ANTES (nucleo/antes_avisos.py): avisar_antigo(item, canal) com if/elif para montar cada canal.
DEPOIS (aqui):
  * Avisador.avisar(item) é o algoritmo comum (monta a mensagem e envia);
  * o passo "qual canal usar" é o MÉTODO FÁBRICA criar_canal(), que cada subclasse sobrescreve;
  * canal novo = produto novo + criador novo; Avisador não muda (OCP).
Quando NÃO usar: um tipo só de canal, ou escolha resolvida por dicionário {nome: Classe} —
em Python dá até para passar a própria CLASSE como parâmetro.
"""


class Canal:
    """PRODUTO: o que todo canal sabe fazer."""

    def enviar(self, destino, mensagem):
        raise NotImplementedError


class CanalEmail(Canal):
    def enviar(self, destino, mensagem):
        return f"[e-mail] para {destino}: {mensagem}"


class CanalSms(Canal):
    def enviar(self, destino, mensagem):
        return f"[sms] {destino}: {mensagem[:60]}"  # SMS tem limite de tamanho


class Avisador:
    """CRIADOR: tem o algoritmo; deixa para a subclasse o MÉTODO FÁBRICA criar_canal()."""

    def criar_canal(self):
        """MÉTODO FÁBRICA: cada subclasse decide QUAL produto (canal) criar."""
        raise NotImplementedError("a subclasse escolhe o canal")

    def avisar(self, item):
        """Monta a mensagem da Destino e envia pelo canal que a subclasse criou."""
        mensagem = f"Confirmação de Destino: R$ {item.total:.2f}"
        canal = self.criar_canal()  # ← o único ponto que muda entre os avisadores
        return canal.enviar(item.cliente, mensagem)


class AvisadorEmail(Avisador):
    def criar_canal(self):
        return CanalEmail()


class AvisadorSms(Avisador):
    def criar_canal(self):
        return CanalSms()


class CanalWhatsapp(Canal):
    """Produto NOVO (extensão): nenhum código existente muda."""

    def enviar(self, destino, mensagem):
        return f"[whatsapp] {destino}: {mensagem}"


class AvisadorWhatsapp(Avisador):
    def criar_canal(self):
        return CanalWhatsapp()
