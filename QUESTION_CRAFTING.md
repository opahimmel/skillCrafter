# Question Crafting Guide
## How to write questions that get precise results from ChromaDB

---

## Why question quality matters

ChromaDB retrieves passages by **semantic similarity** — it finds text that *means something similar* to your question. The more precisely your question matches the vocabulary and structure of your source texts, the better the results.

A vague question returns vague passages. A keyword-dense, concept-anchored question returns the exact paragraphs you need.

**Measured impact on this system:**

| Question quality | Avg. similarity score |
|---|---|
| Simple bullet points | 0.57 – 0.65 |
| RAG-optimized format | 0.65 – 0.74 |
| Best single retrieval | 0.789 |

---

## The two formats

### Format A — Simple (quick start)

```markdown
- What are the core principles of X?
- When does this approach fail?
- What mistakes do beginners make?
```

Good enough for broad topics. Fast to write. Use this when you're exploring a new domain and don't yet know the exact terminology.

---

### Format B — RAG-optimized (recommended)

```markdown
## Section Name

### Q01
**query:** "Concept A vs. Concept B in Domain X: What is the structural difference between A and B,
how does mechanism M explain this, and why does constraint C make approach A preferable under condition Z?"

```yaml
id: Q01
domain: your_domain
subdomain: specific_area
concept_anchor: core_concept_name
keywords:
  - keyword one
  - keyword two
  - keyword three
difficulty: beginner | intermediate | expert
```
```

This is the format that produces scores above 0.70. The structure forces you to write better questions.

---

## The anatomy of a good query

### ✅ Real example (score: 0.789)

```
"Black-Scholes PDE Herleitung über Delta-Hedging-Argument:
Wie konstruiert man ein risikoloses Portfolio aus Option und Basiswert,
welche Black-Scholes Differentialgleichung ergibt sich aus No-Arbitrage,
und welche versteckten Modellannahmen (Transaktionskosten, Volatilität,
Leerverkäufe, Kontinuität) werden dabei implizit gemacht?"
```

What makes this work:
- **Starts with the concept name** — "Black-Scholes PDE" anchors the vector
- **States the method explicitly** — "Delta-Hedging-Argument"
- **Asks multiple sub-questions** — wider semantic coverage
- **Names the constraints** — "Transaktionskosten, Volatilität, Leerverkäufe"
- **No vague pronouns** — every "it" and "this" is replaced with the actual term

---

## The five rules

### Rule 1 — Name the concept explicitly, don't imply it

| ❌ Weak | ✅ Strong |
|---|---|
| "How does the model work?" | "How does the Heston stochastic volatility model work?" |
| "What are the risks?" | "What are the tail risk properties of Gaussian Copula models?" |
| "When does it fail?" | "Under which market conditions does Mean Reversion fail?" |

ChromaDB has no context between questions. Each query must be fully self-contained.

---

### Rule 2 — Use the vocabulary of your sources

Your embedding model creates vectors from the words in your question. If your source uses "äquivalentes Martingalmaß" and your question asks about "risk-neutral probability", the vectors will be closer — but not as close as if you use the exact term.

**Before writing questions:** skim your sources and note the specific terminology they use. Mirror it.

---

### Rule 3 — Pack in contrast and comparison

Questions that compare two things outperform single-concept questions because they match passages that explain *differences and tradeoffs* — the most information-dense parts of any technical text.

```
"ARCH vs. GARCH(1,1) for volatility modeling:
What is the structural difference between ARCH(q) and GARCH(p,q),
why does GARCH(1,1) explain volatility clustering with only three parameters..."
```

vs.

```
"What is GARCH?"
```

The comparison query returns a passage that explains both. The simple query returns a definition.

---

### Rule 4 — Include the failure condition

Technical books spend as much space on *when things break* as on *how things work*. Questions that ask for failure conditions, edge cases, and limitations match those high-value passages.

```
"...und warum ist IGARCH (Integrated GARCH) problematisch für Risikomodelle?"
"...welche versteckten Modellannahmen werden dabei implizit gemacht?"
"...welche Annahmen versagen in realen Hochfrequenzmärkten?"
```

---

### Rule 5 — One concept anchor per question

Each question should have a clear `concept_anchor` — the single most important concept the question is about. This disciplines you to not mix two unrelated ideas into one query.

```yaml
concept_anchor: black_scholes_pde    ✅ clear
concept_anchor: pricing_and_risk     ❌ too broad, two concepts
```

If you have two concept anchors, you have two questions.

---

## Common failure patterns

### Semantic confusion

Some concepts share vocabulary with unrelated concepts. The embedding model can't distinguish them without context.

**Example from this project:**
- Query: "Stopping Time in stochastic control theory"
- Problem: ChromaDB returns "Stop-Loss rules for trading strategies" (score: 0.69)

**Fix:** add disambiguating context to the query:
```
"Stopping Time als mathematisches Konzept in der Filtrations-Theorie F_t,
nicht als Trading Stop-Loss Regel: ..."
```

---

### Preface/introduction matching

Introductory chapters summarize many concepts in one place. A precise question can match a vague introduction with a high score — and return no real content.

**Fix:** use `--min-score 0.65` instead of 0.58 for highly technical domains. High-specificity questions should only surface high-specificity passages.

---

### Source imbalance

A 600-page book will dominate results for every question simply because it has more chunks. The system limits this to **max 2 chunks per source per question**, but your question catalog should still cover the specific sub-topics of each source.

---

## Template

Use this as your starting point for each question:

```markdown
### Q[XX]
**query:** "[Concept A] [vs./in/as] [Concept B] [in Domain/Context]:
[Sub-question 1 — definition or mechanism],
[Sub-question 2 — comparison or derivation],
[Sub-question 3 — failure condition, assumption, or application]?"

```yaml
id: Q[XX]
domain:
subdomain:
concept_anchor:
keywords:
  -
  -
  -
difficulty: expert
```
```

---

## Full example — quantSkill

The `skills/quantSkill/questions.md` catalog in this repo is a fully worked example of 26 RAG-optimized questions across six domains (stochastic calculus, time series, ML for finance, market microstructure, portfolio management, derivatives).

Use it as a reference for structure, depth, and keyword density.
