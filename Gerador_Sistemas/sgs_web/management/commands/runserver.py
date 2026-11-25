"""python manage.py runserver → a tela do SGS, como o `python tela_prompt.py`:

* porta 6100 (o 00) quando nenhuma é dada — os sistemas gerados continuam em 6100+NN;
* ao abrir: estilo cmd, janela de app (pwa), topo e caixas à mostra, sites de uma tela anterior encerrados;
* abre a janela de app (Chrome/Edge num perfil só do SGS) — `--sem-abrir` só sobe o servidor.

Com o autoreload (o padrão do Django), quem prepara e abre a janela é o processo de cima, UMA vez; o processo que
serve (e que reinicia quando um arquivo do SGS muda) só atende. Ao reiniciar ou sair, ele derruba os sites que
subiu (atexit), como o tela_prompt.py faz no Ctrl+C.
"""
import os
import threading

from django.core.management.base import CommandError
from django.core.management.commands.runserver import Command as RunserverDoDjango

import tela_prompt
from sgs_web.views import contexto_do_ambiente


class Command(RunserverDoDjango):
    help = "Sobe a tela do SGS (porta 6100 = o 00) e abre a janela de app; --sem-abrir só sobe o servidor."
    default_port = str(tela_prompt.PORTA_PADRAO)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--sem-abrir", action="store_true", help="não abre a janela (só sobe o servidor)")

    def run(self, **options):
        aberta = os.environ.get(tela_prompt.MARCA_TELA)
        if aberta and os.environ.get("RUN_MAIN") != "true":
            raise CommandError(f"este é o manage.py da PRÓPRIA tela do SGS, que já está aberta (porta {aberta}). "
                               "Para subir um sistema: sgs listar → cd NN → python manage.py runserver")
        # O processo que serve herda isto (o autoreload cria o filho com este ambiente).
        os.environ["SGS_PORTA"] = str(self.port)
        os.environ["SGS_ABRIR"] = "0" if options.get("sem_abrir") else "1"
        if os.environ.get("RUN_MAIN") != "true":            # o processo de cima (ou --noreload): uma vez só
            self._preparar(abrir=not options.get("sem_abrir"))
        super().run(**options)

    def _preparar(self, abrir):
        porta = int(self.port)
        # Antes de mexer em qualquer coisa: com a porta ocupada (outro SGS aberto?), não encerra os sites dele.
        if not tela_prompt.porta_livre(porta):
            raise CommandError(f"a porta {porta} não está livre. Já tem um SGS aberto? "
                               f"Outra porta: python manage.py runserver {porta + 50}")
        ctx = contexto_do_ambiente()
        for linha in tela_prompt.preparar_inicio(ctx):
            self.stdout.write(linha)
        url = f"http://127.0.0.1:{porta}/"
        self.stdout.write(f"{tela_prompt.NOME_SGS} (Django) em {url}")
        self.stdout.write(f"Sistemas gerados em: {ctx.saida}")
        self.stdout.write(f"Configuração (sgs config): {ctx.config.caminho}")
        if abrir:
            def abrir_janela():
                feito = tela_prompt.abrir_no_navegador(url, ctx.config.valores["pwa"])
                self.stdout.write("  " + (feito or f"abra no navegador: {url}"))

            threading.Timer(1.5, abrir_janela).start()       # depois que o servidor já está escutando
