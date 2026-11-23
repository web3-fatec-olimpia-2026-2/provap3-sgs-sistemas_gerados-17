# Cine Olímpia — sistema gerado

> Gerado por `Gerador_Sistemas/gerar_sistema.py` v2.0 — **determinístico, sem IA**: a mesma
> entrada gera sempre os mesmos arquivos. Modo: **só gerar** (sem material de estudo) · **apenas o código** (sem comentários).
> Padrões (12): Encapsulamento com @property, Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor.

## 1. Como o gerador decidiu

Escolha explícita: domínio **cinema**, padrões: encapsulamento, chain, command, interpreter, iterator, mediator, memento, observer, state, strategy, template_method, visitor.

## 2. Mapa dos arquivos

```
nucleo/
  entidades.py              ← Ingresso com @property (base de tudo)
  aprovacao.py
  comandos.py
  regras.py
  colecao.py
  mediador.py
  versoes.py
  eventos.py
  situacao.py
  politicas.py
  fechamento.py
  orcamento.py
tests/
  fabrica.py                ← cria Ingresso válidas para os testes
  test_entidades.py
  test_aprovacao.py
  test_comandos.py
  test_regras.py
  test_colecao.py
  test_mediador.py
  test_versoes.py
  test_eventos.py
  test_situacao.py
  test_politicas.py
  test_fechamento.py
  test_orcamento.py
especificacao.json          ← a entrada usada (dá para editar e regenerar)
```

**Ligações entre os arquivos:**

- `tests/fabrica.py` cria `Ingresso` válidas (`nucleo/entidades.py`) para TODOS os testes
- `nucleo/aprovacao.py` → a cadeia de `Aprovador` lê `item.total`
- `nucleo/comandos.py` → `AlterarCampo` muda a `Ingresso` pelos setters; `Historico` empilha
- `nucleo/regras.py` → `ler_regra` monta `Comparacao`/`E`/`Ou`, que leem campos da `Ingresso`
- `nucleo/colecao.py` → `ColecaoIngresso` guarda `Ingresso`s e entrega `IteradorDeItens`
- `nucleo/mediador.py` → os componentes avisam o `FormularioMediador` (independente da entidade)
- `nucleo/versoes.py` → `EditorIngresso` salva/restaura o estado da `Ingresso` em `Memento`s
- `nucleo/eventos.py` → `IngressoObservavel` embrulha a `Ingresso` e avisa os observadores
- `nucleo/situacao.py` → `SituacaoIngresso` TEM-UMA `Ingresso` e um `Estado`
- `nucleo/politicas.py` → `Cobranca` usa `item.total` da `Ingresso`
- `nucleo/fechamento.py` → `Fechamento.fechar` lê `item.total` da `Ingresso`
- `nucleo/orcamento.py` → `LinhaIngresso` embrulha a `Ingresso`; os visitantes percorrem o `Orcamento`

## 3. Como rodar

Com o `.venv` do projeto ativado (na raiz do projeto: `source .venv/bin/activate`), dentro desta pasta:

```bash
python -m pytest -v
```

## 4. Os padrões deste sistema

| Padrão | Arquivo | Ideia |
|---|---|---|
| Encapsulamento com @property | `nucleo/entidades.py` | O objeto controla o acesso ao próprio estado: cada atributo com regra vira `@property` + setter que valida ANTES de gravar no atributo interno `_nome`; o `__init__` usa `self.x = x` (passa pelo setter); `total` é property CALCULADA, sem setter. |
| Chain of Responsibility | `nucleo/aprovacao.py` | Cada `Aprovador` conhece só a SUA alçada e o PRÓXIMO elo: se pode, aprova; senão, repassa. A cadeia é montada de fora (`encadear`) — incluir ou tirar um nível não mexe nos outros. |
| Command | `nucleo/comandos.py` | Cada ação vira um OBJETO (`AlterarCampo`) que sabe `executar()` e `desfazer()` (guarda o valor anterior). `Historico` (o invocador) empilha os comandos e faz desfazer/refazer em ordem. |
| Interpreter | `nucleo/regras.py` | Cada pedaço da gramática é uma classe com `interpretar(item)`: `Comparacao` (terminal), `E` e `Ou` (não terminais). `ler_regra(texto)` monta a árvore a partir do texto — a regra vira DADO. |
| Iterator | `nucleo/colecao.py` | `ColecaoIngresso` esconde como guarda (dicionário por espectador) e entrega um ITERADOR (`IteradorDeItens`, com `__next__`) em `__iter__`. Percursos especiais (`acima_de`, `ordenados_por_total`) não expõem o interior. |
| Mediator | `nucleo/mediador.py` | Cada componente só conhece o MEDIADOR e avisa `notificar(self, evento)`; `FormularioMediador` decide quem reage (recalcula o resumo, liga/desliga o botão). |
| Memento | `nucleo/versoes.py` | `EditorIngresso` (originador) cria um `Memento` com a cópia do próprio estado e sabe restaurá-lo; `HistoricoDeVersoes` (zelador) só empilha mementos, sem olhar dentro. |
| Observer | `nucleo/eventos.py` | `IngressoObservavel` (sujeito) guarda a lista de observadores e, a cada mudança, chama `atualizar(evento)` em todos. Interessado novo = `inscrever(obj)`; o sujeito não muda. |
| State | `nucleo/situacao.py` | Cada estado é uma classe (`Aberto`, `Confirmado`, `Concluido`, `Cancelado`) que sabe as SUAS transições; `SituacaoIngresso` (contexto) guarda o estado atual e delega. Transição proibida levanta `TransicaoInvalida`. |
| Strategy | `nucleo/politicas.py` | Cada regra vira uma classe com o MESMO método `aplicar(base)`; `Cobranca` (o contexto) RECEBE a política e DELEGA: `self.politica.aplicar(self.item.total)` — sem `if`. |
| Template Method | `nucleo/fechamento.py` | `Fechamento.fechar(item)` é o método TEMPLATE: fixa a ordem dos passos; as subclasses sobrescrevem só o passo que muda (`ajustar`), e o gancho tem padrão vazio. |
| Visitor | `nucleo/orcamento.py` | Cada linha tem `aceitar(visitante)` e chama o método certo do visitante (despacho duplo); cada OPERAÇÃO é um visitante (`CalculoDoTotal`, `TextoDoOrcamento`) com um `visitar_*` por tipo. |
