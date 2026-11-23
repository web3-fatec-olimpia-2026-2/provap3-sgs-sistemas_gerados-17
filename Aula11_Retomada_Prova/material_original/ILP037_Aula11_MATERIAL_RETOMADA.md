# 🔁 Material de Retomada — ILP-037 (pré-P3)
### Aula 11 · 13/11 · para o professor usar **conforme o mapa de lacunas**
### Cada conceito no ciclo **Problema → Conceito → Demonstração → Aplicação** (diretriz §7.1)

> **Como usar.** Não é para dar tudo. Depois do diagnóstico, ataque só os conceitos **🔴 (<40%)** e
> **🟡 (40–70%)**. Cada card abaixo traz um **exemplo NOVO** (diferente do da aula original, como
> pede a §6.1-Passo 4) e termina pedindo ao aluno que **explique** — não só produza. Todos os
> exemplos foram **executados e conferidos**.

---

## Card 1 — Strategy

- **P — Problema real:** o Resort quer calcular a diária com regras diferentes por tipo de hóspede
  (comum, fidelidade, parceiro). Começou com um `if/elif`. Agora Marketing quer somar "pacote
  família" e "alta temporada" — e cada novo tipo obriga a mexer na mesma função.
- **C — Conceito:** **Strategy** encapsula cada "jeito de calcular" numa classe com a mesma
  interface (`calcular`). O contexto (a Reserva) **recebe** a estratégia e delega. Trocar de
  regra = trocar o objeto, não editar o `if`. *Delimitação (Python): se é só uma fórmula simples,
  uma função passada como argumento já é a "estratégia" — não precisa de classe.*
- **D — Demonstração (ao vivo):**
  ```python
  class TarifaFidelidade:
      def calcular(self, diaria): return diaria * 0.9
  class Reserva:
      def __init__(self, diaria, tarifa): self.diaria = diaria; self.tarifa = tarifa
      def total(self): return self.tarifa.calcular(self.diaria)
  print(Reserva(200, TarifaFidelidade()).total())   # 180.0  (conferido)
  ```
- **A — Aplicação orientada (caso novo):** "Criem a `TarifaParceiro` (20% off) **sem tocar** na
  classe `Reserva`. Depois **expliquem**: por que não precisei mexer na Reserva?" *(resposta
  esperada: porque ela depende da interface `calcular`, não do tipo concreto — isso é OCP.)*

---

## Card 2 — SRP / OCP

- **P — Problema real:** uma classe `Reserva` que calcula o preço, **formata** o recibo e ainda
  **grava** em arquivo. Quando muda o formato do recibo, o risco de quebrar o cálculo aparece.
- **C — Conceito:** **SRP** — uma classe, uma razão para mudar (separar cálculo, formatação e
  persistência). **OCP** — aberto para estender (um formato novo), fechado para modificar (não
  reabrir a classe que já funciona).
- **D — Demonstração:** mostrar a `Reserva` inchada e separá-la em `Reserva` (cálculo) +
  `ReciboFormatter` (texto) + `Repositorio` (arquivo). "Quantas razões essa classe tinha para
  mudar? Três. Agora, uma cada."
- **A — Aplicação orientada (caso novo):** "Precisa de um recibo em **JSON** além do texto. Onde
  você mexe? **Explique** por que não precisa reabrir a classe `Reserva`." *(resposta: adiciona um
  novo formatter — OCP.)*

---

## Card 3 — Service × ViewModel (arquitetura / MVVM)

- **P — Problema real:** a tela de quartos decide, no meio do laço, o texto do status, o rótulo do
  botão **e** a regra de negócio (pode reservar?). Para testar a regra, é preciso ler a tela.
- **C — Conceito:** o **Service** separa a **regra de negócio** (o que o sistema *faz*). O
  **ViewModel** separa a **lógica de exibição** (como o dado *aparece*). Os dois tiram lógica da
  tela, mas lógicas **diferentes** — e convivem.
- **D — Demonstração:** mostrar `QuartoViewModel` preparando `status_label`/`botao_label` e um
  `Service` decidindo a tarifa. "O ViewModel pergunta 'como mostro?'; o Service pergunta 'o que é
  verdade no negócio?'."
- **A — Aplicação orientada (caso novo):** "Onde entra a regra 'hóspede com menos de 18 não
  reserva suíte': no Service ou no ViewModel? **Explique.**" *(resposta: Service — é regra de
  negócio, não exibição.)*

---

## Card 4 — Adapter

- **P — Problema real:** o projeto migrou o banco para PostgreSQL/Neon. O driver novo fala
  `execute()/fetch_one()`; o sistema esperava `salvar()/buscar()`. Interfaces incompatíveis.
- **C — Conceito:** o **Adapter** **veste** o objeto incompatível com a interface que o sistema já
  espera, **traduzindo** por dentro. Serve para **uma** peça de terceiro cuja assinatura você não
  controla. *Delimitação: se você controla as duas pontas e são parecidas, duck typing dispensa.*
- **D — Demonstração (conferido):**
  ```python
  class NeonAdapter:
      def __init__(self, c): self._c = c
      def salvar(self, reserva): return int(self._c.execute("INSERT", reserva)["ticket"])
  # salvar(...) devolve 1 (um int), traduzindo o {'ticket': 1} do driver  (conferido)
  ```
- **A — Aplicação orientada (caso novo):** "Chega uma API de pagamento com `cobrar(json)` mas seu
  sistema espera `processar(valor)`. **Explique** por que um Adapter resolve e o que ele traduz."

---

## Card 5 — Facade

- **P — Problema real:** fazer uma reserva chama 4 subsistemas na ordem (disponibilidade, tarifa,
  gravar, notificar). Cada tela que reserva repete essa orquestração.
- **C — Conceito:** a **Facade** cria **um ponto de entrada simples** (`recepcao.reservar(...)`)
  que esconde a orquestração de **vários** subsistemas. Ela **delega**, não reimplementa.
- **D — Demonstração:** mostrar `RecepcaoFacade.reservar()` chamando os quatro por dentro; o
  cliente passa a chamar só a fachada. "A recepção não faz as camas — ela sabe a quem pedir."
- **A — Aplicação orientada (caso novo):** "No checkout, é preciso: fechar a conta + liberar o
  quarto + enviar a nota. **Explique** por que uma Facade de checkout ajudaria — e quando seria
  cerimônia."

---

## Card 6 — Decorator

- **P — Problema real:** somar extras a uma reserva (café, transfer, late checkout) em qualquer
  combinação. Com flags/ifs, cada extra novo mexe na função e nos chamadores.
- **C — Conceito:** o **Decorator** **embrulha** um objeto, **mantém a mesma interface**
  (`preco`/`descricao`) e **soma** a sua parte. Por manter a interface, os embrulhos **empilham**.
  *Delimitação: o `@` do Python decora funções; o padrão decora objetos. Soma fixa → lista basta.*
- **D — Demonstração (conferido):**
  ```python
  ComTransfer(ComCafeDaManha(ReservaBase(200, 2))).preco()   # 520.0  (conferido)
  ```
- **A — Aplicação orientada (caso novo):** "Some um `ComBercoExtra` (+25) **sem alterar** os
  outros decoradores. **Explique** por que a ordem dos extras não muda o total."

---

## 🔗 O fecho que a P3 argui — o trio estrutural

Deixe esta frase na lousa ao fim da retomada (é o que mais confunde e o que a P3 cobra):

> **Adapter** faz *uma* peça **caber** (muda a interface). **Facade** **esconde** *vários*
> subsistemas (cria interface nova). **Decorator** **soma** a *um* objeto e empilha (mantém a
> interface).

---

## ⏱️ Verificação de saída (modelo)

Para cada conceito que ficou 🔴, uma pergunta nova de **explicar** ou **achar o erro**. Exemplos:
- *(Decorator, achar o erro)* "Um colega escreveu `ComCafe(ReservaBase(200,2)).preco()` e devolveu
  200. O que faltou no método `preco` do decorador?" *(somar a parte dele: `... + 40`.)*
- *(Adapter × Facade)* "Em uma frase, por que trocar o banco é Adapter e não Facade?"

Quem continua errando → orientação individual (Teams/e-mail) + registro no caderno de bordo.

---

*Material de Retomada — ILP-037 — FATEC Olímpia — 2026/2 — ciclo P-C-D-A (Diretrizes §7.1). Exemplos executados e conferidos.*
