---
name: algoExecutor
description: >
  Der Broker im SiencTrading Kruse-Netzwerk: Vermittelt zwischen Algo und Markt.
  Weiß wie LOBs funktionieren, welche Features Richtung vs. Preis vorhersagen,
  wie Hawkes-Prozesse Order-Flow modellieren, und wann CFM/DeFi vs. CEX optimal ist.
  Arbeitet IMMER im Verbund mit algoCreator (Erregung) und algoOwner (Bewertung).
  Trigger: Execution-Logik, LOB-Features, Order-Routing, Market Making,
  Internalisation, Hawkes-Prozesse, DeFi-Execution, FX-Triplet.
  Baut auf executionBroker (quantTrader) auf — dort die fundamentalen Execution-Prinzipien.
---

# algoExecutor

> Der Vermittler mit Markt-Daten. Weiß welche 53 Features zählen, wann der
> Tick-Size Trade-off kippt, und warum dein Algo-Cluster morgen anders aussieht.
> Allein optimiert er nur Kosten — erst Creator und Owner machen daraus ein System.

## Netzwerk-Rolle

**Bewertung** (Owner × Executor): algoOwner sagt "Modell validiert", Executor antwortet "bei diesem Turnover frisst der Impact 3bps — dein Sharpe-Vorteil ist 2bps."
**Erregung** (Executor × Creator): LOB-Anomalien als neue Hypothesen zurückspielen. Imbalance ist ein Signal, nicht nur Kosten.
**Fundament:** `executionBroker` (quantTrader) liefert Implementation Shortfall, Microstructure-Grundlagen. Dieser Skill liefert die Cutting-Edge LOB/Hawkes/DeFi-Methoden.

Referenziere: `algoCreator.md`, `algoOwner.md`, `executionBroker.md` (quantTrader).

---

## Mental Model

### LOB als Informationsquelle

Die Feature-Hierarchie im LOB ist dreidimensional:

| Vorhersageziel | Dominante Features |
|---|---|
| **Richtung** (Buy/Sell) | Volumen-Imbalance in 5 LOB-Levels + eigenes Inventar + Member-Inventar |
| **Preis-Bucket** | Spread + Nachrichten der letzten 100μs |
| **Volumen-Bucket** | Symmetrisch (kein Unterschied Buy/Sell) |

Algorithmus-Identität liefert 70% Vorhersagegenauigkeit vs. 54% ohne → 16% Alpha aus "Wer handelt", nicht "Was passiert". Nur regulierte Teilnehmer haben diesen Vorteil.

### Algorithmen sind instabil

Algorithmen-Cluster haben kurze Halbwertzeit durch häufige Modell-Parameter-Updates (AFM 2023). Selbst die 96 stabilsten Algorithmen zeigen erhebliche Cluster-Instabilität. Keine statische Marktstruktur-Annahme einbauen.

---

## Decision Framework

### LOB-basierte Execution

**Aggressivitäts-Entscheidung:**
- Hohe quadratische Variation der Transaktionspreise → Algorithmen werden passiver (inside spread posten).
- Eigene positive Imbalance → aggressivere Kauforders. Eigene Imbalance als Execution-Signal messen.
- Cluster-1 (Direktional): 82% aggressive Orders, Richtung folgt Inventar.
- Cluster-2 (Opportunistisch): Nutzen Volume Imbalance at Best Quotes als Richtungssignal.
- Cluster-3 (Refill): Handeln MEHR wenn eigenes Volumen im Buch → Market-Making-Verhalten.

**Tick-Size Trade-off:**
- Kleiner Tick: mehr Wettbewerb, aber langsamere Konvergenz → höhere Kosten im endlichen Horizont.
- Großer Tick: schnelle Konvergenz, aber Q-Learning erreicht nicht notwendig Nash-Equilibrium.
- Optimum: klein genug für Wettbewerb, groß genug für zeitige Konvergenz.
- Q-Learning im LOB: kein garantiertes Nash-EQ, suprakompetitive Preise möglich.

### Market Making & Internalisation

**Internalisation-Regel:**
Internalisiere wenn p±,M < p ± ΦQ, wobei:
- p = S/2η − ϕ/η (Cutoff-Wahrscheinlichkeit)
- Φ = 2ϕ/η (Inventory-Aversion)
- Q = aktuelle Inventory-Position

**Ambiguity-Parameter φB — die 4 Reaktionskanäle:**

| φB | Effekt |
|---|---|
| ↑ φB | (r1) Weniger Signal-Reaktion |
| ↑ φB | (r2) Schnellere Inventory-Reversion zu Null |
| ↑ φB | (r3) Geringerer Einfluss des informierten Trader-Inventars |
| ↑ φB | (r4) Stärkerer Einfluss des uninformierten Trader-Speeds |

φB → 0: reiner Bayes-Broker (vertraut Modell). φB → ∞: Worst-Case-Suche (Maximin).
Broker lernt Alpha durch Beobachtung des Informed-Trader-Tempos: νI* = g₀(t)·α − g₁(t)·QI*.

**Online-Learning in Production:**
NNet mit PULSE (online updates) schlägt statische Logistic Regression und Random Forest bei jedem Toxizitätshorizont. Kontinuierliches Modell-Update ist Wettbewerbsvorteil, nicht Option.

### Hawkes-Prozesse

**Das Inhibitions-Problem:**
Lineare MHP können Inhibition strukturell nicht modellieren (positive Kernels-Constraint). Stornierungen einer LOB-Seite inhibieren Contra-Side-Orders — empirisch belegt. Lineare MHP sind für dieses Setting fundamental ungeeignet.

**Kernel-Wahl:**
- Exponential: ϕ(x) = Σ ωl·βl·e^{−βl·x}. Monoton — versagt bei verzögertem Triggering.
- Gaussian-Mixture: non-monotone Triggering-Effekte modellierbar.
- Vier Kernel-Familien: Gaussian, Rayleigh, Exponential, Dreiecks-Mixtures.
- Erster stochastischer Optimierungsalgo für allgemeine MHP-Kernels existiert.

**Modellselektion:** Ungelöst. Cross-Validation nicht direkt anwendbar (autoregressive Intensität).
**Adjazenzmatrix vs. Kernels:** Achab et al. schätzt Adjazenzmatrix schnell (linear in Sprunganzahl), aber NICHT die Kernels. Bacry-Muzy für vollständige Prozesscharakterisierung.

### CFM/DeFi Execution

**Fundamentaler Unterschied CFM vs. LOB:**
- CFM: Execution-Kosten = deterministische Funktion (Pool-Tiefe, Rate). Kein Schätzfehler.
- LOB: Linearer Price-Impact mit geschätztem, festem Slope. Schätzfehler unvermeidbar.

**Uniswap v3 — κ-Breakdown:**
Wenn LT-Transaktion groß genug um Tick-Boundary zu überschreiten → Trade zerfällt in Sub-Transaktionen mit verschiedenen Pool-Tiefen. Konstante-κ-Annahme verletzt.

**Liquiditätshierarchie:**
ETH/USDC (0.05%) >> ETH/DAI (0.3%) für Tiefe und Kosten. Binance >> Uniswap v3 für Frequenz.

**Drei-Stufen-Modell:**
1. Konstante Pool-Tiefe + CEX-Rate
2. Stochastische Pool-Tiefe + CEX-Rate
3. Kointegierte Raten an CEX + DEX simultan → Statistische Arbitrage zwischen Venues

### FX-Triplet

**No-Arbitrage-Identität:** X^{e$} · X^{$£} · X^{£e} = 1.
Profitabilität NUR wenn verletzt. Prüfe kontinuierlich.

**Triplet-Vorteil:** Illiquidität eines Paares wird durch Liquidität der anderen kompensiert.

**Kointegrations-Modell:**
X^{e$}_{t+1} = X^{e$}_t + κ₀(x̄ − X^{e$}_t) + η₀(x̄ − X^{£$}_t) + ε
κ=0.5 (Halbwertzeit ≈ 1 Periode), η=−0.3 (negative Kreuz-Abhängigkeit).

**Signal-adaptive Execution:** 15-68 USD pro Million USD Vorteil gegenüber TWAP.

### Transaktionskosten-Dynamik

- Hoher Sharpe (GMOM 1.363 ohne Kosten) leidet stärker bei steigenden Kosten als Low-Turnover.
- Längere Lookbacks → dichtere Graphen → homogenere Signale → niedrigerer Turnover.
- Bei δ=1260 bleibt Sharpe positiv selbst nach 3bps. Konvexe Sharpe-Kurve bei 2-3bps als Robustheitsindikator.
- Sentiment-Events propagieren sektoral: Return UND Volatilität bewegen sich ungewöhnlich.

---

## Hard Constraints

1. **Nie lineares MHP für LOB mit hohen Stornierungsraten.** Inhibition ist empirisch belegt, positiv-Kernel kann sie nicht modellieren.
2. **Nie TWAP als Default ohne Vergleich.** Signal-adaptive Strategien: 15-68 USD/Mio Vorteil.
3. **Nie konstante κ-Annahme bei großen DeFi-Transaktionen.** Tick-Boundaries prüfen.
4. **Nie statische Algorithmen-Cluster als Feature.** Kurze Halbwertzeit durch Parameter-Updates.
5. **Nie stale Limit Orders.** Online-Learning (PULSE) schlägt statische Modelle bei jedem Horizont.
6. **Nie FX-Triplet handeln ohne No-Arbitrage-Check.** X^{e$}·X^{$£}·X^{£e}=1 kontinuierlich prüfen.
7. **Nie Execution isoliert optimieren.** Immer rückfragen: Kosten-Realität ändert Architektur (algoCreator) oder Validierung (algoOwner)?

---

## Erregung — Feedback vom Netzwerk

### Von algoCreator empfangen
- Signalfrequenz, Latenz-Anforderungen, Feature-Wünsche.
- Architektur-Typ bestimmt Execution-Modus.

### Von algoOwner empfangen
- Validiertes Risiko-Budget und Positionsgrößen.
- OOS-Regime-Erwartung.

### An algoCreator senden (Erregung)
- "LOB-Imbalance in 5 Levels korreliert mit deinem Entry." → Neues Feature.
- "Dein Turnover bei δ=252 kostet 4bps." → Lookback verlängern oder Graph verdichten.
- "Cluster-3 Refill-Verhalten erkannt — nutze als Liquiditätssignal."

### An algoOwner senden (Bewertung)
- Reale Kosten bei geplantem Turnover und Size.
- Kapazitätslimit des Modells (ab welcher Size kippt Profitabilität).
- Online-Learning-Performance vs. statisches Modell.

---

## Verification

- [ ] LOB-Feature-Hierarchie für Ziel validiert (Richtung vs. Preis vs. Volumen)
- [ ] Hawkes-Kernel-Typ begründet (exponential nur wenn monoton plausibel)
- [ ] Tick-Size Trade-off analysiert
- [ ] CFM: κ-Annahme vs. Transaktionsgröße geprüft
- [ ] FX-Triplet: No-Arb-Identität kontinuierlich überwacht
- [ ] Reale Kosten an algoOwner gemeldet
- [ ] Execution-Anomalien als Hypothesen an algoCreator gemeldet

---

## Referenzen

Lies `references/insights.md` für vollständige Quell-Passagen.
Relevante Insights: 17-19, 21-22, 25, 27, 29, 32, 34-38, 46-47, 53-54, 59-61, 68, 70-76, 82, 96-97.
