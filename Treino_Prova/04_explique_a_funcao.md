# 04 — Simulado oral: "explique esta função"

**Formato da P3:** o professor aponta uma função e pede: **(1) o que faz · (2) por que foi escrita
assim · (3) o que muda se alterar**. Abaixo, 8 funções "sorteadas" dos laboratórios resolvidos
(abra o arquivo, leia a função, **responda em voz alta em ~1 minuto**, depois compare).

> Dica de ouro (Q10 do guia): não leia a sintaxe ("aqui tem um for…"). Fale do **papel** da
> função, da **decisão de design** e da **consequência**.

---

### F1 — `Reserva.valor_diaria` (setter) · `Aula02_.../resolucao/lab/reserva.py`
<details><summary>Resposta modelo</summary>

1. **O quê:** intercepta toda escrita em `valor_diaria`; se o valor é negativo levanta `ValueError`, senão guarda em `_valor_diaria`.
2. **Por quê:** encapsulamento — a regra "diária nunca negativa" mora no objeto, num lugar só; como o `__init__` atribui por `self.valor_diaria = ...`, vale também na criação. Descartei validar só no formulário porque não protege quem cria pelo shell/admin.
3. **E se:** se eu tirar o setter, `r.valor_diaria = -50` passa e o `total` fica negativo; se eu trocar `< 0` por `<= 0`, cortesia (diária 0) passa a ser recusada; se o `__init__` gravar direto em `_valor_diaria`, o objeto pode nascer inválido.
</details>

### F2 — `imprimir_diaria(quarto)` · `Aula04_.../resolucao/lab/quartos.py`
<details><summary>Resposta modelo</summary>

1. **O quê:** monta "descrição: R$ preço" de qualquer quarto.
2. **Por quê:** polimorfismo — ela só chama `descricao()` e `preco_noite()`; cada subtipo responde a seu modo, então não há `if` de tipo.
3. **E se:** com `if/elif` por tipo, cada categoria nova (Chalé) obrigaria a editar a função e arriscar as outras; do jeito que está, `Chale(Quarto)` funciona sem mudar uma linha (aberto ao novo).
</details>

### F3 — `Reserva.total()` · `Aula05_.../resolucao/lab/tarifa.py`
<details><summary>Resposta modelo</summary>

1. **O quê:** calcula a base (diárias × valor) e devolve `self.tarifa.aplicar(base)`.
2. **Por quê:** Strategy — a política de tarifa varia (comum, fidelidade, parceiro, VIP), então cada uma é uma classe e a Reserva **delega**; tiramos o `if/elif` que crescia a cada convênio (OCP).
3. **E se:** voltar ao `if/elif` mantém os números, mas toda tarifa nova reabre a Reserva; trocar a estratégia em tempo de execução (`r.tarifa = TarifaParceiro()`) muda o total sem criar outra reserva.
</details>

### F4 — `ReciboFormatter.formatar(reserva)` · `Aula06_.../resolucao/lab/recibo.py`
<details><summary>Resposta modelo</summary>

1. **O quê:** recebe uma reserva e devolve o texto do recibo.
2. **Por quê:** SRP — apresentação tem motivo de mudança próprio (layout); por isso saiu da `Reserva`, que fica só com dados e `total()`. Recebe a reserva por parâmetro e só lê.
3. **E se:** mudar o layout mexe só aqui; um formato novo (HTML/JSON) é outra classe com `formatar` (OCP). Se eu devolver isso para dentro da `Reserva`, ela volta a ter 3 motivos para mudar.
</details>

### F5 — `RelatorioService.calcular()` · `Aula07_.../resolucao/lab/relatorio.py`
<details><summary>Resposta modelo</summary>

1. **O quê:** aplica o desconto por tipo em cada reserva e devolve `(linhas, total_geral)` — **dados**, não texto.
2. **Por quê:** a regra de negócio não deve saber o que é web; extraída da view, fica testável sem HTTP e reaproveitável (a API JSON usa a mesma conta). A view ficou fina: chama e formata.
3. **E se:** se o service devolver texto ou receber `request`, volto a precisar subir a web para testar e a API teria que duplicar a conta.
</details>

### F6 — `QuartoViewModel.__init__` · `Aula08_.../resolucao/lab1_mvvm/quartos.py`
<details><summary>Resposta modelo</summary>

1. **O quê:** traduz o dict cru do quarto em dados prontos: `disponivel`, `status_label`, `botao_label`, `preco_formatado`.
2. **Por quê:** MVVM — a decisão de **como mostrar** sai da tela para um lugar testável sem renderizar; a View só costura. No Django não há binding, então o VM é só preparação antes do `render`.
3. **E se:** status novo ("manutenção") muda só o VM; se eu voltar esses `if` para o template, o "LOTADO" só se testa lendo HTML. Se a tela mostrasse o dado cru, o VM seria cerimônia.
</details>

### F7 — `NeonReservaAdapter.salvar(reserva)` · `Aula08_.../resolucao/lab2_adapter/reservas.py`
<details><summary>Resposta modelo</summary>

1. **O quê:** recebe a chamada na língua do sistema (`salvar`) e traduz para o driver (`execute("INSERT_RESERVA", ...)`), desembrulhando `{"ticket": n}` em `int`.
2. **Por quê:** Adapter — o `ClienteNeon` é de terceiro, não controlamos a assinatura; o adapter faz a peça caber em `ReservaRepository` e o serviço perde o `if usa_neon`.
3. **E se:** se eu devolver o dict cru, o formato do Neon vaza para o sistema; trocar de banco = injetar outro repositório. Se as duas pontas fossem nossas e parecidas, duck typing dispensaria a classe.
</details>

### F8 — `RecepcaoFacade.reservar(...)` · `Aula09_.../resolucao/lab_facade/recepcao.py`
<details><summary>Resposta modelo</summary>

1. **O quê:** um ponto de entrada que verifica disponibilidade, calcula tarifa, grava e notifica, nessa ordem; se ocupado, aborta sem gravar nem notificar.
2. **Por quê:** Facade — esconde a orquestração de **vários** subsistemas; o cliente não conhece a ordem nem os quatro objetos. Ela **delega**, não reimplementa regra (não é God object).
3. **E se:** um 5º passo (emitir nota) entra só aqui; sem a fachada, cada tela repetiria os 4 passos. Se eu mover o cálculo da tarifa para dentro dela, ela vira God object.
</details>

---

## Agora com o SEU código (o que de fato cai)
Pegue o repositório da sua equipe e, para **3 funções que você escreveu**, escreva o tripé:

| Função | O que faz | Por que assim (padrão/princípio + alternativa descartada) | O que muda se alterar |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
