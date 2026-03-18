---
name: algo-trading-builder
description: >
  Aktiviere diesen Skill wenn der User einen Trading-Algorithmus baut, entwickelt,
  designt oder implementiert — von Grund auf oder als wesentliche Überarbeitung.
  Auch bei Architektur-Entscheidungen ("LSTM oder TFT?", "RL oder nicht?"),
  Backtest-Design, Deployment-Fragen oder Signal-Konstruktion für Trading-Systeme.
  Greife proaktiv wenn Begriffe wie "Strategie bauen", "Modell entwickeln",
  "Algorithmus designen", "deployen", "backtesten", "Signal konstruieren",
  "Execution designen" im Kontext von algorithmischem Trading erscheinen.
---

# Algo Trading Builder

Dieser Skill führt durch den Aufbau eines Trading-Algorithmus von der ersten
Designentscheidung bis zum Deployment. Destilliert aus 22 akademischen Papers
(2020–2025) über RL-Finance, Execution, Signal Construction und Marktmikrostruktur.

---

## Mental Model

Baue nicht zuerst das Modell — baue zuerst das Verständnis der Umgebung in der
das Modell leben soll.

Die drei Fragen die ein Experte zuerst stellt:
1. **Wie viel Signal ist überhaupt vorhanden?** (Signal-to-Noise-Ratio, price informativeness ξ)
2. **In welchem Regime befinde ich mich — und wie stabil ist es?**
3. **Was ist mein Execution-Kontext?** (LOB, CFM/DeFi, FX, Volumen-Klasse)

Erst danach folgen Architektur-, Signal- und Execution-Entscheidungen.

---

## Decision Framework

### Schritt 1 — Umgebung messen

Messe bevor du baust:

- **Noise-Trading-Risiko σu**: Werden Preise durch informiertes Handeln oder Noise getrieben? Hohes σu → RL versagt strukturell durch Q-Value-Asymmetrie. Nicht behebbar durch mehr Exploration.
- **Price Informativeness ξ**: Wie stark reagieren Preise auf Fundamentals? Niedriges ξ → Exploration liefert irreführende statt korrektive Signale. Exploration-Exploitation-Tradeoff bricht zusammen.
- **Non-Stationaritätsdimension**: In welcher Dimension ist das System nicht-stationär — Volatilität, Korrelationslänge, Mean-Reversion-Länge, oder Kombination? Jede Dimension erfordert eine andere Antwort.

Wenn σu hoch UND ξ niedrig: **kein RL**. Nutze regelbasierte oder robuste Optimierungsansätze.

---

### Schritt 2 — Strategie-Typ wählen

| Typ | Haupt-Branch | Schlüssel-Konzepte |
|---|---|---|
| Momentum / Signal-based | A + B + D | DMN, Network Momentum, Shrinkage |
| Execution / Market Making | A + C | LOB-Features, Internalisation, Hawkes |
| FX / Statarb | E | RDMM, Triplet-Kointegration, Robustheit |
| Portfolio Construction | D | HAR-DRD, GHAR, Kovarianzmodellierung |

---

### Schritt 3 — Architektur wählen

Wähle nach Krisentyp-Exposition und SNR-Umgebung:

- **Endogene Krisen** (graduell, Vorlaufsignal wie 2008): LSTM + online CPD-Modul (Bayesian GP)
- **Exogene Schocks** (plötzlich, ohne Vorlaufsignal wie COVID): TFT — stabiler über Regime, aber hyperparametersensitiver
- **Momentum in Low-SNR**: Decoder-Only Transformer. Der Informer ist für Zeitreihen mit Periodizität konzipiert — Momentum-Märkte haben zu niedrigen SNR. Convolutional Transformer scheitert aus demselben Grund.
- **Allgemein robuste Wahl**: TFT als All-Rounder, LSTM für kurzfristige Muster

Wenn Momentum-Performance 2015–2020 einbricht: prüfe Factor Crowding. Gleiche Modelle = koordinierte Positionen = gegenseitige negative Externalitäten. CPD-Modul mildert dies signifikant.

---

### Schritt 4 — Signal konstruieren

**Kovarianzmodellierung:**
- Trenne Volatilität und Korrelation — sie haben **verschiedene optimale Lookback-Horizonte**. Volatilität: kurzfristig dominant. Korrelation: mittelfristig dominant. Ein einheitliches Fenster für beide ist strukturell suboptimal.
- Nutze DRD-Dekomposition: Ht = Dt·Rt·Dt (Diagonal-Rotation-Diagonal). Trennt Volatilitäten von Korrelationen. Überlegen gegenüber Cholesky-Zerlegung (Bollerslev 2018).
- Modelliere Cross-Asset-Spillovers mit GHAR: vt = Self-Terms + γ·W·Neighbor-Terms, W = O^{-1/2}·A·O^{-1/2}. Nutze Graphical LASSO für den Graphen: Θ̂ = argmin[Tr(SΘ) − log det(Θ) + λΣ|Θjk|]

**Shrinkage:**
- Wende Ledoit-Wolf-Shrinkage an: Σ̂ = (1−δ)·S + δ·N⁻¹·Tr(S)·I
- δ ist **zeitvariabel** — kein universeller optimaler Wert existiert. δ≥0.5 funktioniert für Large-Cap-Equities bis 2015, danach adaptive Optimierung per Validierungsfenster.

**Network Momentum:**
- K=5 Graphen mit Lookback δ∈{252,504,756,1008,1260} Tage als Ensemble: Ā = (1/K)·ΣA^(k)
- δ=252 treibt den Großteil der Profitabilität. δ=1008 und δ=1260 sind nahezu redundant (Korrelation 0.93) — überprüfe ob beide nötig sind.
- Ziel: 1-Tag volatilitätsskalierter Return. Ein einziges Modell für alle Assets (cross-sectional pooling).

**In-Sample-Bias:**
- In-Sample-Sharpe ist strukturell optimistisch: Jensen's Inequality garantiert E[in-sample return] ≥ out-of-sample. Ursache: (1) Singular-Werte überschätzt, (2) Singular-Vektoren falsch ausgerichtet. Shrink beides.

---

### Schritt 5 — Execution designen

**LOB-basiert:**
- Feature-Hierarchie für Vorhersage: Richtung = Volumen-Imbalance in 5 LOB-Levels + eigenes Inventar. Preis-Bucket = Spread + Nachrichten der letzten 100ms. Volumen-Bucket = symmetrisch (kein Buy/Sell-Unterschied).
- Eigene positive Imbalance → aggressivere Kauforders. Miss eigene Imbalance als Execution-Signal.
- Algorithmen-Cluster haben kurze Halbwertzeit durch häufige Modell-Updates. Baue keine statische Marktstruktur-Annahme ein.

**Hawkes-Prozesse im LOB:**
- Lineare MHP können Inhibition strukturell nicht modellieren (positive Kernels-Constraint). Inhibitionsverhalten ist in LOBs empirisch gut belegt (Stornierungen einer Seite inhibieren Contra-Side-Orders).
- Nutze Gaussian-Mixture-Kernels für non-monotone Triggering-Effekte.
- Modellselektion für MHP ist ungelöst — Cross-Validation nicht direkt anwendbar durch autoregressive Intensitätsform.

**CFM/DeFi:**
- CFM-Kosten sind deterministisch (Funktion von Pool-Tiefe und Rate) — kein Schätzfehler.
- κ-Annahme (konstante Pool-Tiefe) versagt wenn ein großer LT-Trade eine Tick-Boundary in Uniswap v3 Concentrated Liquidity überschreitet.
- CEX-LOB: linearer Price-Impact mit festem Slope (Schätzung aus historischen Daten nötig).

**FX-Execution:**
- Nutze FX-Triplet statt einzelnes Paar wenn ein Kurs illiquide ist. Illiquidität eines Paares wird durch Liquidität der anderen beiden kompensiert — signifikant bessere Performance.
- Profitabilität setzt Verletzung der No-Arbitrage-Identität X^(e$)·X^($£)·X^(£e)=1 voraus. Prüfe diese Bedingung kontinuierlich.

---

### Schritt 6 — Validieren

Nutze **Expanding-Window-Backtest**: Hyperparameter-Optimierung bei jeder Iteration neu durchführen auf dem erweiterten Fenster — nicht einmalig zu Beginn.

Lookback-Suchraum für Momentum: {10, 21, 63, 126, 252} Tage. Optimiere auf Validierungsverlust pro Fenster, nicht auf In-Sample-Performance.

Stratifiziere Out-of-Sample: ruhige Periode (untere 90% der realisierten Volatilität) vs. turbulente Periode (obere 10%). Graph-basierte Modelle liefern größere Verbesserungen im turbulenten Regime — nutze das als Qualitätssignal.

---

### Schritt 7 — Deployment

Folge dem 5-Stufen Deployment-Ladder — kein Schritt darf übersprungen werden:

1. Ground-truth-Generator (validiere Lernfähigkeit des Modells grundsätzlich)
2. Historische Daten mit Walk-Forward oder Rolling Validation
3. Paper Trading auf realer Infrastruktur (Interactive Brokers / QuantConnect / Alpaca)
4. **Shadow PnL** — Algorithmus läuft parallel zum Live-System, generiert PnL ohne echte Trades
5. Limited-stakes Live-Deployment

Schritt 4 ist nicht optional. Real-time Training ist in der Praxis nicht machbar. Das steady-state Verhalten aus der Shadow-Phase ist die einzige zuverlässige Vorhersage des Live-Verhaltens.

---

## Hard Constraints

1. **Kein RL bei hohem σu ohne vorherige Messung.** Q-Value-Asymmetrie ist strukturell: Noise-Verluste erzeugen permanenten Downward-Bias, Noise-Gewinne werden durch Exploitation korrigiert — das Ungleichgewicht ist asymmetrisch und nicht durch mehr Exploration behebbar.

2. **Nie In-Sample-Sharpe als Entscheidungskriterium.** Jensen's Inequality garantiert strukturelle Überschätzung. Out-of-Sample-Validation mit echtem Hold-out ist Pflicht.

3. **Nie lineares MHP für LOB mit hohen Stornierungsraten.** Inhibitionsverhalten ist empirisch belegt und strukturell nicht modellierbar mit positiven Kernels.

4. **Nie festes Shrinkage-δ.** Es ist zeitvariabel — ein fixer Wert erzeugt garantierte Fehlallokation in bestimmten Marktphasen.

5. **Nie TWAP als Default-Execution ohne Vergleich.** Signal-adaptive Strategien liefern 15–68 USD pro Million USD Vorteil gegenüber TWAP in FX.

6. **Nie live deployen ohne Shadow-PnL-Phase.**

7. **Nie Factor Crowding ignorieren** wenn ein populäres Modell eingesetzt wird. Gleiche Modelle → koordinierte Positionen → gegenseitige negative Externalitäten (empirisch 2015–2020).

---

## Verification

Nach dem Bauen prüfe:

- [ ] σu und ξ gemessen — Architekturwahl darauf begründet?
- [ ] Expanding-Window-Backtest mit Hyperparameter-Reoptimierung pro Fenster?
- [ ] Out-of-Sample stratifiziert (ruhig vs. turbulent)?
- [ ] In-Sample-Sharpe explizit disqualifiziert?
- [ ] Shrinkage δ zeitvariabel optimiert?
- [ ] Factor-Crowding-Check durchgeführt?
- [ ] Shadow-PnL-Phase vor Live-Deployment geplant?

---

## Referenzen

Vollständige Quell-Passagen mit Formeln, Parametern und Paper-Herkunft:
→ `references/insights.md` — 98 Excellence-Chunks aus 22 Papers (2020–2025)
