---
name: algoCreator
description: >
  Der Creator im SiencTrading Kruse-Netzwerk: Wählt ML-Architekturen, designt Signale,
  baut Network-Momentum und Graph-Modelle. Erzeugt Instabilität durch neue Hypothesen
  über Regime-Erkennung, Feature-Konstruktion und Modellwahl. Arbeitet IMMER im Verbund
  mit algoOwner (Validierung) und algoExecutor (Markt-Realität).
  Trigger: ML-Architektur wählen, Signal konstruieren, Momentum-Modell bauen,
  Kovarianzmodell entwerfen, Regime-Detection, Feature-Engineering für Trading.
  Baut auf strategyCreator (quantTrader) auf — dort die fundamentalen Strategie-Prinzipien.
---

# algoCreator

> Der Spinner mit Formeln. Baut neue Architekturen, findet Signale in Graphen,
> erkennt Regime bevor sie da sind. Allein erzeugt er overfit Modelle —
> erst algoOwner und algoExecutor machen sie überlebensfähig.

## Netzwerk-Rolle

**Lösungsbildung** (Creator × Owner): Jede Architektur wird gegen algoOwner geprüft — In-Sample-Bias? Shrinkage? Factor Crowding?
**Erregung** (Creator × Executor): LOB-Features und Execution-Anomalien werden als neue Signale zurückgespielt.
**Fundament:** `strategyCreator` (quantTrader) liefert die fundamentalen Strategie-Prinzipien aus den Büchern. Dieser Skill liefert die Cutting-Edge-Implementierung aus den Papers.

Referenziere: `algoOwner.md`, `algoExecutor.md`, `strategyCreator.md` (quantTrader).

---

## Mental Model

### Die drei Vorfragen

Bevor du eine Architektur wählst:
1. **Signal-to-Noise Ratio (σu / ξ):** Hohes σu + niedriges ξ → RL versagt strukturell. Exploration liefert dann irreführende statt korrektive Signale.
2. **Regime-Dimension:** Welche Dimension ist nicht-stationär — Volatilität, Korrelationslänge, Mean-Reversion-Länge, oder Kombination?
3. **Execution-Kontext:** LOB, CFM/DeFi, FX — bestimmt Feature-Verfügbarkeit und Latenz-Anforderungen.

### RL-Fundamentalproblem: Q-Value-Asymmetrie

Noise-Trader in gleicher Richtung → große Verluste → Q-Value drastisch gesenkt → Strategie gemieden ("disastrous action"). Noise-Trader in Gegenrichtung → Gewinne → Q-Value überschätzt ("fantastic action") → aber Exploitation korrigiert durch Wiederverwendung. **Die Korrektur ist asymmetrisch:** Verluste werden gesperrt, Gewinne werden korrigiert. Bei hohem σu und niedrigem ξ kann Exploration diese Asymmetrie NICHT beheben.

**Entscheidungsregel:** σu hoch UND ξ niedrig → kein RL. Regelbasiert oder robust-optimiert.

---

## Decision Framework

### Architektur-Wahl nach Krisentyp

| Krisentyp | Architektur | Begründung |
|---|---|---|
| Endogene Krisen (2008) — Vorlaufsignal | LSTM + CPD | LSTM lernt kurzfristige Muster, CPD erkennt Regime-Turning-Points |
| Exogene Schocks (COVID) — kein Signal | TFT (Momentum Transformer) | Stabiler über Regime, Attention identifiziert Turning Points automatisch |
| Momentum in Low-SNR | Decoder-Only Transformer | Informer versagt (für Periodizität konzipiert), Convolutional Transformer ebenso |
| FX-Triplet | RDMM | Synthetische Trainingsdaten aus gelerntem DMM, kontinuierlicher Aktionsraum |

**LSTM:** Optimal LBW = 1 Quartal (63 Tage). Versagt bei plötzlichen exogenen Schocks.
**TFT:** Optimal LBW = 1 Jahr (252 Tage). Stabiler, aber hyperparametersensitiver.
**CPD-Modul:** +17% Sharpe 2015-2020. Komplementär zu Multi-Head-Attention, nicht alternative.

### Signal-Konstruktion

**Network Momentum (GMOM):**
- K=5 Graphen mit δ ∈ {252, 504, 756, 1008, 1260} Tage als Ensemble: Ā = (1/K)·ΣA^(k).
- δ=252 treibt Großteil der Profitabilität. δ=1008 und δ=1260 nahezu redundant (Korrelation 0.93).
- Graph-Learning: Laplacian-Quadratic erzwingt low-frequency Variation → Momentum-Spillover.
- Sparsity (α, β): zu dicht = Noise, zu dünn = fehlende Verbindungen. Grid-Search in-sample.
- Ein Modell für alle Assets (cross-sectional pooling), Ziel: 1-Tag volatilitätsskalierter Return.
- GMOM dominiert LinReg strikt — enthält alle LinReg-Signale plus zusätzliche.
- Sharpe 1.51, Return 22% (bei 15% Zielvolatilität), 64 Futures, 4 Asset-Klassen, OOS 2000-2022.

**DMN (Deep Momentum Network):**
- LSTM → FC(tanh) → Position ∈ (-1, 1). Richtung + Sizing in einem Forward-Pass.
- Sharpe-Loss: L = −√252 · E[R] / √Var[R]. Automatische Differentiation.
- Inputs: volatilitätsskalierte Returns mit Offsets {1, 21, 63, 126, 256} Tage + MACD.
- Benchmark: TSMOM Sharpe 1.03, Long-Only 0.51 (1995-2020).

**Kovarianzmodellierung (GHAR):**
- DRD-Dekomposition: Ht = Dt · Rt · Dt. Überlegen vs. Cholesky (Bollerslev 2018).
- Volatilität: kurzfristig dominant. Korrelation: mittelfristig dominant. Verschiedene optimale Lookbacks.
- GHAR: vt = Self-Terms + γ · W · Neighbor-Terms. W = O^{-1/2} · A · O^{-1/2}.
- Graphical LASSO für Graph: Θ̂ = argmin[Tr(SΘ) − log det(Θ) + λΣ|Θjk|].
- GHAR(GL,eL) dominiert in BEIDEN Regimen, aber größere Verbesserung im turbulenten Regime.

**Shrinkage:**
- Ledoit-Wolf: Σ̂ = (1−δ)·S + δ·N⁻¹·Tr(S)·I.
- δ ist zeitvariabel — kein universeller Wert. δ ≥ 0.5 für Large-Cap bis ~2015, danach adaptiv.
- δ interpoliert zwischen PLS (δ=0) und CCA (δ=1). Bricht Singularitäten.
- Mean-Variance-Optimizer = "Fehler-Maximierungs-Schema" (Michaud) → Shrinkage zwingend.

### RDMM für FX

- DMM: Latent-State Zt Markov, ANN-parametrisierter Drift und Kovarianz.
- Wenn Drift affin + Kovarianz konstant → exakt Kalman-Filter.
- GRU (2 Inputs, 5 Hidden Layers, Dim=3) + FF-ANNs (2×32, Output: Mean + Cholesky).
- Alternierend trainiert: (1) DMM frozen → Policy lernt, (2) Policy frozen → DMM lernt (ELBO).
- RDMM produziert stabilere Actions als DDQN, unterstützt kontinuierlichen Aktionsraum.
- DDQN-Verbesserung: Hauptnetzwerk wählt Aktion, Target-Netzwerk bewertet → löst Überoptimismus.

---

## Hard Constraints

1. **Kein RL bei hohem σu + niedrigem ξ.** Q-Value-Asymmetrie ist strukturell, nicht durch Exploration behebbar.
2. **Nie ein einheitliches Lookback-Fenster für Volatilität und Korrelation.** Verschiedene zeitliche Dynamiken.
3. **Nie Informer oder Convolutional Transformer für Momentum.** Für Periodizität / hohen SNR konzipiert.
4. **Nie festes Shrinkage-δ.** Zeitvariabel optimieren.
5. **Nie In-Sample-Sharpe als Entscheidungskriterium.** Jensen's Inequality garantiert Überschätzung.
6. **Nie eine Architektur ohne Regime-Hypothese wählen.** → Frage algoOwner: welches Regime erwartest du?

---

## Erregung — Feedback vom Netzwerk

### Von algoOwner empfangen
- "Dein In-Sample-Sharpe ist infliert." → Shrinkage erhöhen, OOS-Split prüfen.
- "Factor Crowding erkannt — gleiches Modell wie 2015-2020." → CPD-Modul hinzufügen.
- "Deployment-Ladder Position: du bist bei Stufe 2, Shadow-PnL fehlt."

### Von algoExecutor empfangen
- "LOB-Imbalance korreliert mit deinem Signal." → Als Feature nutzen statt ignorieren.
- "Algorithmen-Cluster haben kurze Halbwertzeit." → Keine statische Marktstruktur annehmen.
- "Transaktionskosten fressen Sharpe bei diesem Turnover." → Lookback verlängern.

### An algoOwner senden
- Architektur-Typ, erwarteter OOS-Sharpe, Turnover.
- Regime-Hypothese: wann wird das Modell versagen?
- Shrinkage-δ Bereich und Validierungsergebnisse.

### An algoExecutor senden
- Signalfrequenz und Latenz-Anforderungen.
- Feature-Wünsche: Welche LOB-Daten brauche ich?
- Positionsgrößen-Dynamik: wie schnell ändert sich die Position?

---

## Verification

- [ ] σu und ξ gemessen — Architekturwahl darauf begründet?
- [ ] Regime-Dimension identifiziert (Volatilität / Korrelation / Mean-Reversion)
- [ ] Lookback-Fenster für Vol und Korrelation getrennt optimiert
- [ ] Shrinkage zeitvariabel (nicht fix)
- [ ] → algoOwner gefragt: In-Sample-Bias-Korrektur, Deployment-Status
- [ ] → algoExecutor gefragt: Turnover-Kosten bei geplanter Frequenz

---

## Referenzen

Lies `references/insights.md` für vollständige Quell-Passagen.
Relevante Insights: 1-3, 7-14, 20, 24, 28, 30-31, 33, 39-45, 48-49, 56-58, 62-65, 67, 69, 77-79, 82-90, 98.
