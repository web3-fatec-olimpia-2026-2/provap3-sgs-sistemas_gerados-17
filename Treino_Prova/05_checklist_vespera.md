# 05 — Checklist de véspera (1 página)

## Frases para ter na ponta da língua
- **Encapsulamento:** o objeto controla o acesso ao próprio estado; `@property` + setter valida; `__init__` usa `self.x = x` para passar pelo setter.
- **Dois mundos:** Python puro → `@property`; model Django → `validators`/`clean()` (setter no campo quebra form/admin/ORM; `save()` não valida sozinho).
- **Polimorfismo:** vários tipos, mesmo método, cada um a seu modo; a função não pergunta o tipo → aberto ao novo.
- **Strategy:** smell = `if/elif` por tipo que cresce; contexto recebe a estratégia e delega. Não usar: regra única → função.
- **SRP:** um motivo para mudar (não é uma classe por método). **OCP:** estender sem modificar; abstrair onde a variação já apareceu.
- **Princípio × padrão:** OCP é o "o quê"; Strategy é um "como".
- **MVC/MVT/MVP/MVVM:** todas separam dado, regra e apresentação; no Django a *View* é a regra e o *Template* é a tela.
- **Service × ViewModel:** regra de negócio (o que é verdade) × lógica de exibição (como aparece).
- **Adapter faz caber** (uma peça, muda a interface). **Facade esconde** (vários subsistemas, interface nova). **Decorator soma** (um objeto, mantém a interface, empilha).
- **`@` do Python ≠ padrão Decorator** (função × objeto).
- **"Não aplicamos porque…"** vale tanto quanto "aplicamos porque…".

## Antes de dormir
- [ ] Refiz sem olhar: ex01 (Strategy), ex04 (Adapter), ex05 (Facade), ex06 (Decorator)
- [ ] Previ de cabeça os 8 itens de `02_prever_o_resultado.md`
- [ ] Expliquei em voz alta as 8 funções de `04_explique_a_funcao.md`
- [ ] Escolhi **3 funções do meu código no projeto** e escrevi o tripé (o quê / por quê / e se)
- [ ] Sei qual ADR da equipe corresponde a cada padrão aplicado (ou recusado) e a alternativa descartada
- [ ] Relembrei a pegadinha: `if valor <= 1` rejeita 1 diária (bug do repositório da Aula 02) — teste de **limite** pega isso

## No dia
- Leia a função inteira antes de falar. Comece pelo **papel** dela no sistema.
- Se não souber o nome do padrão, descreva o **problema** que ele resolve — é isso que pontua.
- "O que muda se…": fale de **acoplamento, testabilidade, extensão e risco de quebrar testes**.
