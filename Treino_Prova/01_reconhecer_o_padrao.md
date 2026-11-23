# 01 — Reconhecer o padrão (pelo smell)

Para cada cenário: **qual padrão/princípio cabe** (ou "nenhum") e **por quê em 1 frase**.
Lembre: a P3 valoriza dizer **"não cabe"** quando não cabe.

1. Uma função `calcular_desconto(cliente)` tem `if cliente.tipo == "estudante" ... elif "idoso" ... elif "servidor"` e o comercial pede um tipo novo por mês.
2. O app usa uma lib de SMS cujo método é `send_text(to, body, sender_id)`, mas todo o sistema chama `notificador.enviar(destino, mensagem)`.
3. Para abrir uma conta, a view chama: validar CPF → consultar score → criar usuário → criar carteira → mandar e-mail de boas-vindas. A mesma sequência existe na API e no admin.
4. Uma pizza pode ter borda recheada, queijo extra, bacon extra e entrega por moto, em qualquer combinação, e cada extra muda preço **e** descrição.
5. A classe `Relatorio` busca dados no banco, calcula médias e gera o PDF.
6. O template do Django tem `{% if pedido.status == "P" %}Pendente{% elif ... %}` e calcula "ATRASADO" comparando datas.
7. Na view `checkout`, o cálculo do total com cupom e frete está no meio do código que monta o `render(...)`; para testar o cupom é preciso simular um POST.
8. O sistema sempre cobra a mesma taxa de serviço de 10% de todo mundo; alguém propôs criar `TaxaServicoStrategy`.
9. Uma tela "Sobre nós" mostra nome e telefone da empresa exatamente como estão no banco; alguém quer criar um `SobreViewModel`.
10. A equipe controla as duas classes `RepositorioMemoria` e `RepositorioSQLite`, e as duas já têm `salvar()` e `buscar()`. Alguém quer criar um `SQLiteAdapter`.
11. Uma "fachada" `Loja` tem 40 métodos e implementa ela mesma o cálculo de frete, de imposto e o envio de e-mail.
12. Um `@login_required` em cima de uma view do Django: é o padrão Decorator do GoF?

---
---

## Gabarito

1. **Strategy** — `if/elif` por tipo que cresce a cada regra nova: cada desconto vira uma classe com `calcular`, o contexto delega (OCP).
2. **Adapter** — uma peça de terceiro com interface diferente (`send_text`) que precisa caber na interface que o sistema já usa (`enviar`).
3. **Facade** — vários subsistemas em ordem fixa, repetidos em 3 clientes; `AberturaContaFacade.abrir(...)` concentra a orquestração e delega.
4. **Decorator** — opcionais combináveis que mantêm a interface (`preco`/`descricao`) e somam; empilha sem explosão de subclasses ou flags.
5. **SRP** — três motivos para mudar (dados, cálculo, PDF): separar em repositório, serviço de cálculo e gerador de PDF.
6. **ViewModel (MVVM)** — decisão de exibição (rótulo do status) e estado derivado ("ATRASADO") presos no template; um VM prepara `status_label`/`atrasado` e testa sem renderizar. (Se "atrasado" for regra de negócio usada em outros lugares, o cálculo vai num Service e o VM só traduz.)
7. **Service** (arquitetura MVT + camada de serviço) — a regra está presa na camada web; extrair `CheckoutService.total(...)` testável sem HTTP.
8. **Nenhum** — comportamento único que não varia: Strategy seria cerimônia; uma constante/função resolve.
9. **Nenhum** — exibição trivial (dado como está): ViewModel seria cerimônia.
10. **Nenhum (duck typing)** — você controla as duas pontas e as interfaces já coincidem; Adapter formal é cerimônia.
11. **Facade mal aplicada → God object** — a fachada deve **delegar**, não implementar regra; separar os subsistemas (SRP) e deixar a fachada só orquestrar.
12. **Não** — o `@` do Python decora **funções** (callables) em tempo de definição; o padrão GoF decora **objetos** em tempo de execução. Mesma ideia de "embrulhar", mecanismos diferentes.
