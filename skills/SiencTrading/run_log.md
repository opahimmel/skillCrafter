# Run Log: SiencTrading

---

## Run 1 — 2026-03-18

**Fragen:** 25
**Passagen gefunden (STARK, ≥0.7):** ~150+ (alle Fragen hatten STARK-Treffer)
**Als Exzellenz bewertet:** 20
**Neue Insights in insight.md:** 20

### Was funktioniert hat

- **Fragen 1, 6, 10** (Failure-Modus RL/ML) → Exzellente Passagen aus `w34054.pdf` über Q-Value-Asymmetrie und AI-Kollusion. Diese Quelle ist ein echter Goldschatz.
- **Fragen 16, 23** (Regime Change / Non-Stationarität) → Sehr starke Treffer aus `2105.13727v3.pdf` und `2112.08534v3.pdf` über CPD, GP-basierte Regime-Erkennung und Transformer-Attention.
- **Fragen 9, 17** (Backtesting-Gaps / Deployment) → `ssrn-5703882.pdf` lieferte konsistent gute Passagen über den Deployment-Ladder und methodische Schwächen.
- **Fragen 13, 15** (Position Sizing / Signal Capacity) → `2202.10817v4.pdf` lieferte mathematisch präzise Insights über CCA-Shrinkage und Jensen-Bias.
- **Frage 12** (Transaction Costs) → `ssrn-4105954.pdf` und `ssrn-4144743.pdf` lieferten kontraintuitive Tick-Size und CFM-Execution Insights.

### Was nicht funktioniert hat

- **Frage 24** (Genuine edge vs data-mining) → Nur Scores um 0.80 erreicht, keine klaren Mechanismus-Passagen. Die Treffer waren theoretische Spieltheorie-Passagen ohne direkte Operationalisierung.
- **Frage 22** (Dominant alpha sources evolution) → Zu generelle Review-Passagen, kein quellenspezifisches Ergebnis. Frage zu breit gestellt.
- **Frage 18** (Alternative data) → Passagen zeigen nur dass alternative Daten genutzt werden, aber kein Mechanismus warum/wie sie Edge erzeugen.
- **Frage 2** (What experts know vs beginners) → Trifft hauptsächlich Regulatory/Surveillance Content, nicht Skill-relevante Passagen.
- **Frage 7** (Portfolio optimization breakdown) → Gute Score-Zahlen, aber Passagen blieben auf dem Niveau von "DL verbessert Portfolio-Optimierung" ohne konkreten Failure-Mechanismus.

### Wissenslücken erkannt

1. **Execution Quality**: Wie misst man konkret ob ein Algorithmus gut oder schlecht ausführt? VWAP/TWAP vs adaptive Execution — `ssrn-4144743.pdf` hat AMM-Execution (DeFi), aber was ist mit traditionellen LOBs?
2. **Signal Decay Measurement**: Wie misst man empirisch wann ein Signal seinen Edge verliert? Kein Chunk hat eine konkrete Methodik geliefert.
3. **Live System Architecture**: Was sind die konkreten technischen Entscheidungen (Latenz, Order-Routing, State Management) beim Aufbau eines Live-Systems? Frage 25 hat nur generische Passagen geliefert.
4. **DeFi vs TradFi**: `ssrn-4144743.pdf` ist stark auf AMMs/CFMs fokussiert — ein separater Bereich mit anderen Mechanismen. Unklar wie viel davon auf TradFi übertragbar ist.
5. **Risk Sizing in Production**: Wie skaliert man Position Sizing unter realen Liquiditätsbedingungen? Kein Chunk hat das quantitativ behandelt.

### Hypothesen für Run 2

- "At what spread-to-volatility ratio does aggressive execution become suboptimal?" → könnte tiefere Passagen aus `ssrn-4442770.pdf` und `ssrn-4265814.pdf` triggern
- "How do practitioners measure signal decay in production systems?" → direktere Frage als "when does signal stop working"
- "What is the optimal rebalancing frequency given transaction costs and signal halflife?" → spezifischer als die bisherige Frage zu trading frequency
- "How does inventory risk interact with signal alpha in market making?" → könnte `ssrn-4597879.pdf` und `ssrn-4265814.pdf` besser ausschöpfen
- "What are the specific failure modes of expanding window backtests?" → Follow-up zu INSIGHT-20
- "Under what conditions does AI collusion in trading harm vs help individual algorithm returns?" → Follow-up zu INSIGHTs 01-03

---
## Run 2 — 2026-03-18

**Fragen:** 24
**Passagen gefunden (STARK):** alle Fragen hatten STARK-Treffer
**Als Exzellenz bewertet:** 16
**Neue Insights in insight.md:** 16 (INSIGHT-21 bis INSIGHT-36)

### Was funktioniert hat

- **Frage 4** (Inventory Aversion Parameter) → Top-Score 0.90 aus `ssrn-4597879.pdf`. Exakte Formel für Internalisation-Entscheidung.
- **Frage 18** (Tick Size Q-Learning) → 0.90 und 0.90 aus `ssrn-4105954.pdf`. Drei konkrete Findings über Q-Learning-Konvergenz — ergänzt INSIGHT-17 aus Run 1.
- **Frage 3** (Price-Trigger Breakdown) → 0.91, beste Score des Runs. Weitere Tiefe aus `w34054.pdf` über low-ξ Bedingung.
- **Fragen 16, 17** (Covariance robustness / MVO breakdown) → `2202.10817v4.pdf` lieferte präzise Mechanismus-Insights über eigenvector-betting und double-bias.

### Was nicht funktioniert hat

- **Frage 7** (Signal Alpha Decay Measurement) → Keine konkrete Messmethodik gefunden.
- **Frage 21** (Capacity Constraint empirisch) → AMM/LOB-Passagen ohne operative Capacity-Definition.
- **Frage 22** (Non-negotiable Risk Controls) → Nur Regulatory-Text (ESMA), keine quantitativen Grenzen.
- **Frage 11** (Slippage compounding) → Parameter-Misspecification statt Slippage-Compounding.

### Wissenslücken erkannt

1. **Hawkes-Prozesse**: `ssrn-3969208.pdf` hat MHP-Fitting-Algorithmen — noch nicht ausgeschöpft.
2. **Network Momentum**: `2011.06430v2.pdf` und `2308.11294v1.pdf` — NLP/Netzwerk-Momentum noch kaum berührt.
3. **Realized Covariance Forecasting**: `ssrn-4274989.pdf` Graph LASSO + Line Graph — noch nicht extrahiert.
4. **FX Triplet Arbitrage**: `ssrn-3812473.pdf` — illiquid-pair-Kompensation durch Triplet noch nicht tief extrahiert.

### Hypothesen für Run 3

- "How does Hawkes process intensity estimation fail in markets with high cancellation rates?" → `ssrn-3969208.pdf`
- "What is the graph-based structure used for realized covariance matrix forecasting and what does it outperform?" → `ssrn-4274989.pdf`
- "How does news/sentiment network momentum combine with price momentum — what is the sign of the reversal effect?" → `2308.11294v1.pdf`
- "What are the specific LOB features that predict whether a limit order will be executed or cancelled?" → `ssrn-4442770.pdf`
- "How does the RL simulation-to-live gap specifically manifest in multi-agent environments with partial observability?"

---
## Run 3 — 2026-03-18

**Fragen:** 20
**Passagen gefunden (STARK):** alle 20 Fragen hatten STARK-Treffer (≥0.83)
**Als Exzellenz bewertet:** 22
**Neue Insights in insight.md:** 22 (INSIGHT-37 bis INSIGHT-58)

### Was funktioniert hat

- **Fragen 1, 2** (Hawkes-Inhibition) → Goldtreffer aus `ssrn-3969208.pdf` Chunk #83. Lineares MHP fundamentally ungeeignet für LOB-Daten — keine schnelle Kalibrierung für nicht-lineare Hawkes. Klar operationale Konsequenz.
- **Frage 3** (Wiener-Hopf) → `ssrn-3969208.pdf` Chunk #5 lieferte präzise Methodenlandschaft: Achab schnell aber nur Adjazenzmatrix, nicht Kernels. Genau die Trennlinie die praktisch entscheidend ist.
- **Fragen 6, 7** (Network Momentum Reversal + Graph-Mechanismus) → `2308.11294v1.pdf` Chunks #82, #14, #32 — drei exzellente Passagen. Laplacian-Quadratic-Term als Mechanismus, K=5 Ensemble mit konkreten δ-Werten, OLS-Reversal-Debatte gelöst.
- **Frage 8** (Kovarianz-Architektur) → `ssrn-4274989.pdf` Chunk #12 lieferte die nicht-intuitive Asymmetrie: Volatilität = kurzfristig, Korrelation = mittelfristig.
- **Fragen 12, 13** (FX Triplet) → `ssrn-3812473.pdf` Chunks #9, #8 — beide exzellent. No-Arb-Identität X^e$*X^$£*X^£e=1 als mathematische Bedingung für Profitabilität.
- **Fragen 14** (RDMM vs DDQN) → Chunk #64 und #48 lieferten Architekturdetails und den DMM-Simulations-Mechanismus.
- **Frage 15** (Over-Pruning Bedingungen) → Top-Scores: Chunk #128 (0.8927) und #190 (0.8365). Exploration-Exploitation-Tradeoff als Gleichgewichtsschalter, plus vollständiger Feedback-Loop-Mechanismus über alle Marktzustände.
- **Frage 16** (LOB Features) → `ssrn-4442770.pdf` Chunk #106+105 — Klare Hierarchie: Richtung = Imbalance/Inventar, Preis = Spread. Direkt operationalisierbar.
- **Fragen 20** (TFT vs LSTM) → `2112.08534v3.pdf` Chunk #38+39 — Endogen/exogen-Unterscheidung (2008 vs COVID), Informer-Failure-Mechanismus (Periodizität-Annahme). Beide 5/5.

### Was nicht funktioniert hat

- **Frage 4** (Hawkes Decay-Parameter β) → Keine direkte Antwort. `ssrn-4265814.pdf` lieferte einen Midprice-α-Signal-Mechanismus, aber nicht den β-Decay in Relation zu Liquidität. Frage zu spezifisch für das verfügbare Quellenmaterial.
- **Frage 10** (Line-Graph-Transformation) → Nur Duplikate von Chunk #13 der bereits anderen Fragen aufgetaucht war. Kein dedizierter Chunk zur Line-Graph-Notwendigkeit. Die Frage adressiert einen Aspekt der in der Quelle nur indirekt behandelt wird.
- **Frage 11** (Marktbedingungen für Graph-Kovarianz) → Chunk #87 lieferte die turbulente vs ruhige Periode (gut), aber Chunk #96 nur Robustheitstests ohne neue Mechanismen.
- **Frage 17** (Cluster Stability vs Market Quality Metrics) → Chunk #118 lieferte Instabilitätsmechanismus (Parameter-Updates), aber keine direkten Verbindungen zu Spread/Depth/Price-Informativeness wie gefragt.
- **Frage 18** (Adaptive Robust Failure) → Chunk #12 gab Zeitkonsistenz-Mechanismus (gut, 4/5), aber kein konkreter Failure-Punkt "wann versagt es trotz genug Lernzeit."

### Wissenslücken erkannt

1. **Hawkes β-Decay und Liquidität**: Welche empirischen Studien zeigen den Zusammenhang zwischen Marktliquidität und der Zerfallsrate von Hawkes-Kernels?
2. **Line-Graph-Transformation**: Warum ist die Line-Graph-Transformation für Kovarianz-Forecasting notwendig? (In `ssrn-4274989.pdf` angedeutet aber nicht direkt gefischt)
3. **Adaptive Robust Failure Threshold**: Wann genau (welche Lernzeit / welche Marktbedingungen) schlägt die adaptive Robust-Strategie die Fixed-Interval-Strategie nicht?
4. **Broker-Ambiguity Model**: `ssrn-4265814.pdf` hat φ_B-Parameter und Ambiguity-Aversion — diese Quelle kaum erschlossen.
5. **FX Triplet Co-Movement Mechanismus**: Die statistische Arbitrage auf Co-Bewegungen noch nicht tief extrahiert (Chunk #10 angedeutet).
6. **AMM/DeFi Liquidations**: `ssrn-4144743.pdf` hat konkrete Parameter-Schätzungen für ETH-Pools — spezifischer DeFi-Bereich noch nicht ausgeschöpft.

### Hypothesen für Run 4

- "What is the specific role of the line graph transformation when converting realized covariance to a graph structure and why does it enable better prediction?" → `ssrn-4274989.pdf` direkt
- "How does the ambiguity aversion parameter φB in the broker's optimization problem determine when to externalise vs internalise — what is the exact threshold?" → `ssrn-4265814.pdf`
- "What is the statistical co-movement structure exploited in FX triplet statistical arbitrage and how is the spread defined?" → `ssrn-3812473.pdf` tiefer fischen
- "Under what signal-to-noise conditions does the adaptive robust acquisition strategy outperform the standard robust strategy, and what is the minimum learning window?" → `ssrn-3571991.pdf`
- "How does the graph learning model for network momentum handle the case where the Laplacian graph signal assumption is violated in crisis periods?" → `2308.11294v1.pdf`
- "What are the specific LOB features from `ssrn-4442770.pdf` that predict volume bucket conditional on direction — does the feature hierarchy change?" → noch nicht direkt gefragt
- "What is the specific kernel structure used in ssrn-3969208.pdf's proposed estimation method and how does it differ from exponential kernels?" → tieferer Dive in MHP-Paper
- "How does the RDMM in `ssrn-3812473.pdf` model the statistical spread of the FX triplet and what is the learned state space structure?" → RDMM + FX-Statistik kombinieren

---
## Run 4 — 2026-03-18

**Fragen:** 21
**Passagen gefunden (STARK):** alle 21 Fragen hatten STARK-Treffer (≥0.82)
**Als Exzellenz bewertet:** 21
**Neue Insights in insight.md:** 21 (INSIGHT-59 bis INSIGHT-79)

### Was funktioniert hat

- **Frage 1** (Kernel-Struktur MHP) → `ssrn-3969208.pdf` Chunk #16 + #80 — Gaussian Mixture Kernels als Alternative zu Exponential für non-monotone Order-Flow-Triggering. Erster stochastischer Optimierungsalgorithmus für allgemeine Kernels.
- **Frage 3** (Model Selection) → Chunk #82: Cross-Validation für MHP ungeklärt wegen auto-regressiver Form. Wichtige offene Lücke.
- **Frage 4** (Line-Graph) → `ssrn-4274989.pdf` Chunk #37 — Endlich die Line-Graph-Erklärung! Kovarianz-Dekomposition: Volatilität + Korrelation getrennt, Neighborhood-Aggregation über Graphen.
- **Frage 5** (GL-Zielfunktion) → Chunk #34: Exakte Zielfunktion des Graphical LASSO mit Tr(SΘ)-logdet+λ-Penalty.
- **Frage 5+** (Quantifizierung) → Chunk #64: 2.5%/2.5%/1.8% Verbesserung, Additivität von Vol-Graph + Korr-Graph gezeigt.
- **Frage 6** (LE/LF vs LQ Asymmetrie) → Chunk #88+89 — Exakte Erklärung: QLIKE robust gegen Extremwerte, LE/LF dominiert von wenigen Ausreißern. Top-Score 0.8929.
- **Fragen 10, 11, 12** (Broker φB) → `ssrn-4265814.pdf` Chunks #64, #38, #37 — Vollständige Charakterisierung: vier Reaktionskanäle, Grenzwertverhalten φB→0/∞, Lernmechanismus aus Informed-Trader-Flow.
- **Frage 8** (RDMM Latent State) → `ssrn-3812473.pdf` Chunk #34 — Vollständige mathematische DMM-Struktur: Markov-Latent-State, ANN-parametrisiert, reduziert auf Kalman-Filter.
- **Frage 9** (DDQN vs RDMM) → Chunk #63 + 2308.11294 Chunk #79: DDQN noisiger; RDMM kontinuierlicher Aktionsraum. Network-Momentum: Sharpe 1.511, Return 22.2%, MDD 19.9%, δ=252 treibt profitability.
- **Fragen 15, 17** (LOB Features) → Chunk #108 + #148: Feature-Hierarchie vollständig: Spread=Preis nicht Richtung; Nachrichten-100µs=Preis; Volumen symmetrisch. Cluster-3-Anomalie: eigenes Volumen = mehr Aktivität.
- **Frage 18** (CFM vs LOB) → `ssrn-4144743.pdf` Chunk #34: Deterministischer CFM-Execution-Cost vs linearer LOB-Impact. Fundamentale Architektur-Differenz.
- **Fragen 20, 21** (Signal-Kombination) → TFT optimal bei 1-Jahr-Input (LSTM=1-Quartal), CPD +17% Sharpe 2015-2020. GMOM dominiert LinReg strikt (enthält alle OLS-Signale plus eigene).

### Was nicht funktioniert hat

- **Frage 2** (Hawkes Branching Ratio + Market Impact) → Keine direkte Verbindung zwischen Branching Ratio und Market Impact gefunden. Frage zu präzise für das verfügbare Material.
- **Frage 7** (FX Triplet Cointegration) → Chunks hauptsächlich Duplikate von Run 3. Die formale Cointegrations-Definition wurde nicht tief extrahiert.
- **Fragen 13, 14** (Adaptive Robust Failure Threshold) → Keine konkrete minimale Lernzeit oder Prior-Bedingung gefunden. Nur Wiederholung der "enough time to learn"-Bedingung ohne Quantifizierung.
- **Frage 19** (DeFi Pool Depth Threshold) → Keine spezifische Pool-Depth-Ratio gefunden ab der DeFi gegenüber LOB profitabler wird. Empirische Vergleichsdaten für ETH-Pools gefunden, aber kein Crossing-Point.

### Wissenslücken erkannt

1. **Adaptive Robust: Quantitative Bedingung** — Wann genau hat der Agent "genug Zeit"? Was ist die formale Bedingung (Signal-zu-Rausch-Verhältnis des Drift-Lernens)?
2. **FX Triplet: Formale Cointegration** — Wie wird das statistische Spread zwischen den drei Paaren formal definiert und durch welche Schätzung gemessen?
3. **DeFi vs LOB: Crossing Point** — Unter welchen Pool-Tiefe-Bedingungen wird DeFi-Execution zu einer sinnvollen Alternative?
4. **Broker Signal Learning: Performance** — Wie gut lernt der Broker das α-Signal tatsächlich? Welche Metriken werden verwendet?
5. **Network Momentum: Out-of-Sample Robustness** — Wie verhält sich das Network-Momentum-Modell in Regimen die nicht im Training-Set sind?

### Hypothesen für Run 5 (Letzter Run — Lückenschluss)

- "What is the formal condition on the signal-to-noise ratio of drift estimation that determines when adaptive robust outperforms fixed-interval robust?" → `ssrn-3571991.pdf` tiefer
- "How is the co-movement spread between FX pairs in a triplet formally estimated in statistical arbitrage and what is the mean-reversion half-life?" → `ssrn-3812473.pdf` Statarb-Abschnitt
- "What is the out-of-sample backtesting methodology used for network momentum — what test set periods, metrics, and benchmark strategies?" → `2308.11294v1.pdf`
- "What is the role of the constant pool depth assumption in the DeFi liquidation model and when does it break down?" → `ssrn-4144743.pdf`
- "How do HAR-DRD models decompose covariance into DRD structure and what is the specific parameterization?" → `ssrn-4274989.pdf` — noch nicht tief extrahiert
- "What is the learning architecture in DMN (Deep Momentum Network) and how does it simultaneously learn trend estimation and position sizing?" → `2112.08534v3.pdf` + `2105.13727v3.pdf` vertiefend
- "What is the specific price-trigger strategy structure (η, ω, T triple) and how does it characterize implicit coordination among AI speculators?" → `w34054.pdf` noch tiefer

---

## Run 5 — 2026-03-18

**Fragen:** 20
**Passagen gefunden (STARK):** 20
**Als Exzellenz bewertet:** 19
**Neue Insights in insight.md:** 19 (INSIGHT-80 bis INSIGHT-98)

### Was funktioniert hat
- Adaptive Robust: Direkte Fragen nach Simulationsparametern (T, θ*) trafen ssrn-3571991 Chunk #85 präzise — numerische Parameterwerte erhalten.
- FX Triplet Cointegration: Frage nach formaler Gleichungsstruktur lieferte vollständige Kointegrations-Gleichung aus ssrn-3812473 mit κ=0.5, η=-0.3.
- DRD-Dekomposition: Score 0.9047 — beste Retrieval-Qualität des gesamten Loops. Ht=DtRtDt formal exakt aus ssrn-4274989 Chunk #29.
- DMN-Architektur und Sharpe-Loss: Beide Fragen trafen 2105.13727v3 präzise — vollständige Architekturspezifikation und exakte Verlustfunktion.
- Price-Trigger: Zwei Fragen (Struktur + Bedingung) trafen w34054 Chunks #87 und #97 mit Scores 0.8936/0.9101 — top 3 Scores des gesamten Loops.
- CFM κ-Bedingung: Tick-boundary-Breakdown für Uniswap v3 CL aus ssrn-4144743 Chunk #91 erstmals vollständig extrahiert.
- Network Momentum Backtest: Exakte Spezifikation aus 2308.11294v1 Chunk #20 — 64 Futures, 4 Asset-Klassen, 2000-2022.

### Was nicht funktioniert hat
- Adaptive Robust SNR-Kondition: Formale Bedingung SNR(μ̂) nicht explizit in den Quellen — ssrn-3571991 liefert nur Simulationsparameter, keine geschlossene SNR-Formel. Lücke bleibt.
- FX Statarb Sharpe/PnL-Metriken: RDMM vs. DDQN numerischer Vergleich nicht direkt extrahiert — ssrn-3812473 enthält keine explizite Benchmark-Tabelle mit Sharpe-Werten für RDMM vs. DDQN.
- In-sample R-squared HAR-DRD: ssrn-4274989 liefert keine explizite R²-Tabelle im Retrieved-Text — Chunk #29 fokussiert auf Dekomposition, nicht auf Modellgüte.
- Cross-Asset Performance Network Momentum: Stärkste/schwächste Asset-Klasse nicht in den Passagen — Chunk #20 spezifiziert nur Gesamt-Backtesting-Setup, keine Asset-Klassen-Aufschlüsselung.

### Wissenslücken erkannt
- **Adaptive Robust SNR-Formel**: Kein formaler Vergleich von adaptiver vs. fixer Strategie in geschlossener Form in den Quellen gefunden. Möglicherweise nur durch numerische Simulation demonstriert.
- **HAR-DRD R²-Improvement**: Quantitativer Verbesserungsnachweis durch Graph-Prädiktoren fehlt in den extrahierten Passagen.
- **AI-Koordinationsdynamik (Lernmechanismus)**: Wie genau das Lernspiel zur Price-Trigger-Gleichgewicht konvergiert — nur Proposition 3.1 explizit, keine Lernmechanismus-Beschreibung.
- **FX RDMM vs. DDQN Performance-Zahlen**: Numerischer Vergleich nicht in Retrieved-Chunks.

### Hypothesen für weiteren Run (falls WEITER)
- Frage direkt nach "signal-to-noise ratio" + "adaptive robust" in ssrn-3571991 könnte numerische Sensitivitätsanalyse finden statt geschlossener Formel.
- Frage nach "Sharpe ratio" + "RDMM" + "DDQN" könnte explizite Benchmark-Tabelle aus ssrn-3812473 treffen.
- Frage nach "R-squared" + "HAR" + "graph" könnte Modellgüte-Sektion aus ssrn-4274989 treffen.
- Frage nach "learning" + "price-trigger" + "convergence" könnte Lernmechanismus-Sektion aus w34054 treffen.

---
