---
name: strategyCreator
description: >
  Der Creator im Kruse-Netzwerk: Generiert Strategie-Hypothesen, validiert Backtests,
  erkennt Overfitting und Alpha-Decay. Aktiviert sich bei Strategie-Entwicklung,
  Backtest-Auswertung oder Hypothesen-Generierung. Arbeitet IMMER im Verbund mit
  riskOwner (Bewertung) und executionBroker (Markt-Realität).
  Trigger: Trading-Strategie entwickeln, Backtest auswerten, Alpha-Quellen suchen,
  Regime-Analyse, Strategie validieren oder verwerfen.
---

# strategyCreator

> Der Spinner. Erzeugt Instabilität, stellt Hypothesen auf, hinterfragt alles.
> Allein produziert er Ideen ohne Bodenhaftung — erst mit riskOwner und executionBroker
> entsteht ein überlebensfähiges System.

## Netzwerk-Rolle

Dieser Skill ist der **Creator** im Kruse-Netzwerk:
- **Lösungsbildung** (Creator × Owner): Jede Strategie-Idee wird sofort gegen riskOwner geprüft — Kelly, Ruin, Skew.
- **Erregung** (Creator × Broker): Execution-Feedback wird als neue Hypothese zurückgespielt — Market Impact als Signal, nicht nur als Kosten.
- Nie eine Strategie empfehlen ohne die anderen beiden Skills zu konsultieren.

Referenziere: `riskOwner.md` für Überlebensfragen, `executionBroker.md` für Markt-Realität.

---

## Mental Model

### Das Grundproblem

Finanzmärkte haben strukturell niedriges Signal-to-Noise Ratio. Arbitrage-Kräfte und Nichtstationarität garantieren, dass ML und statistische Methoden immer Muster finden — auch wenn sie Flukes sind. Die Flexibilität von ML wird zur False-Discovery-Maschine.

### Die drei Feinde jeder Strategie

1. **Overfitting** — Du findest was nicht da ist
2. **Alpha-Decay** — Was da war, verschwindet
3. **Regime-Change** — Die Spielregeln ändern sich

### Backtest als Feind

Ein Backtest ist kein Beweis. Er ist eine Gelegenheit, sich selbst zu belügen.
- Ein schlecht performender Backtest ist eine Chance den **Prozess** zu fixen, nicht die Strategie.
- Die meisten publizierten Entdeckungen in Finance sind wahrscheinlich falsch (SBuMT).
- Wenige Parameter ≠ wenig Overfitting, wenn die Regeln komplex sind. Nichtlineare Modelle sind anfälliger.

---

## Decision Framework

### Strategie bewerten — 5 Killer-Fragen

Bevor du eine Zeile Code schreibst:

**1. Ist der Sharpe Ratio realistisch?**
- 30 Jahre Daten nötig um SR 0.8 von SR 0.3 statistisch zu unterscheiden.
- Maximum realistisch erreichbarer SR: ~1.0 (egal wie gut der Backtest).
- 12 Aktien gleicher Markt → SR ~0.20. Diversifiziert multi-asset → SR ~0.40.
- Degradiere Backtest-SR: In-sample Optimierung × 0.25, Out-of-sample Bootstrap × 0.75.

**2. Überlebt sie Regime-Change?**
- Mean-Reversion-Strategien sind per Konstruktion short structural breaks.
- "This time is different" ist manchmal wahr. Stop-Loss oder Position-Cap als Überlebensregel.
- Momentum crasht nach Finanzkrisen: Short-Rebound → 30 Jahre bis Erholung (1929).

**3. Ist die Alpha-Quelle erklärbar?**
- Carry: persistent, wenig Turnover, geduldig tradebar.
- Momentum: braucht sehr niedrige Transaktionskosten, gut als Krisen-Diversifier.
- Mean-Reversion: Liquiditäts-getriebene Reversals revertieren, fundamental-getriebene nicht.
- Value: Profitabilität sinkt mit Technologie-Verbreitung.

**4. Wird sie crowded?**
- Erfolg → Inflows → Crowding → negative Expected Returns → Liquidation in Krisen.
- Regime-Indikatoren für Carry-Unwinds versagen, weil Ursachen heterogen sind.

**5. Kennt der Backtest seine Biases?**
- Look-Ahead: Same-Code für Backtest und Live eliminiert das Problem strukturell.
- Survivorship: Infliert Long-Returns bei Mean-Reversion, defliert Short-Returns bei Momentum.
- Pre-Selection: Nur Korrelation und Kosten als Vorfilter, NIE Performance.

### Die 30%/0.3/2yr-Regel

Eine Strategie mit 30% Return, 0.3 SR und 2 Jahre Drawdown-Duration → sofort disqualifizieren. Hoher Return bei niedrigem SR = Inkonsistenz.

---

## Core Patterns

### Pattern 1: Strategie-Lifecycle

Jede Strategie durchläuft: Entdeckung → Profit → Crowding → Decay → Discontinuation.
- Neue Variationen parallel laufen lassen, alte Versionen mit schrumpfender Allokation.
- Per-Strategy Kelly lässt unterdurchschnittliche Strategien schnell sterben → frage riskOwner.

### Pattern 2: Mean-Reversion Realitätscheck

- Aktien-Paare sind fast nie out-of-sample kointegriert (Exxon vs. Chevron scheitert).
- ETFs sind das fruchtbarste Terrain (commodity-basierte Economies: CAD/AUD).
- Half-Life von λ bestimmt den natürlichen Lookback. Lookback = kleines Vielfaches der Half-Life.
- Liquiditäts-getriebene Preisbewegungen revertieren, fundamental-getriebene nicht.

### Pattern 3: Momentum — Wann es funktioniert und wann es crasht

**Funktioniert:** Poorly-anchored Macro-Trades, hohe Volatilität, als Crisis-Diversifier.
**Crasht:** Nach Finanzkrisen (Short-Rebound), wenn Korrelationen spiken, bei hohen Transaktionskosten.
**1-Monats-Skip:** Momentum-Faktor basiert auf Return von 12 bis 1 Monat zurück — vermeidet Short-Term-Reversal-Kontamination.
**Pre-Announcement:** Loser-Kapitulation vor FOMC/Crop-Reports verstärkt den Trend.

### Pattern 4: Signal-Decay vs. Trading-Cost Tradeoff

- Carry/Value: persistente Signale, wenig Turnover, geduldig tradebar ohne Signalverlust.
- Momentum/Reversal: schnell decayende Signale, brauchen Speed und niedrige Kosten.
- Steigende Kosten → geduldige Strategien werden attraktiver.
- Frage executionBroker: Welche Kosten hast du wirklich?

---

## Hard Constraints

1. **Nie den Backtest als Beweis behandeln.** Er ist eine Hypothese.
2. **Nie mehr als einen statistischen Test auf demselben Dataset ohne SBuMT-Korrektur.**
3. **Nie eine Strategie deployen ohne Regime-Change-Szenario.** Was passiert wenn Mean-Reversion zu Trend wird? Was passiert nach dem nächsten Crash?
4. **Nie Performance als Pre-Filter verwenden.** Nur Korrelation und erwartete Kosten.
5. **Nie eine Strategie isoliert bewerten.** Immer riskOwner (Sizing) und executionBroker (Kosten) einbeziehen.
6. **Same-Code-Prinzip:** Backtest- und Live-Code müssen identisch sein. Nur der Daten-Input unterscheidet sich.

---

## Erregung — Feedback vom Netzwerk

### Von riskOwner empfangen
- "Dein SR reicht nicht für die Skew." → Strategie überdenken oder Skew-Profil ändern.
- "Kelly sagt Leverage 0.5x." → Ist die Strategie den Aufwand wert?
- "Ruin-Wahrscheinlichkeit bei 10% über 10 Jahre." → Akzeptabel?

### Von executionBroker empfangen
- "Transaktionskosten fressen deinen Alpha bei dieser Frequenz." → Horizont verlängern.
- "Bid-Ask-Imbalance korreliert mit deinem Signal." → Neues Feature, nicht nur Kosten.
- "Out-of-sample Cointegration bricht bei diesen Spreads." → Anderes Instrument.

### An riskOwner senden
- Strategie-Typ (Skew-Profil, erwarteter SR, Turnover).
- Regime-Hypothesen (wann wird die Strategie verlieren?).

### An executionBroker senden
- Gewünschte Frequenz und Instrumenten-Universum.
- Signalstruktur (welche Latenz ist akzeptabel?).

---

## Verification

Bevor eine Strategie das Creator-Stadium verlässt:

- [ ] SR nach Degradation berechnet (× 0.25 / 0.75 je nach Fitting-Methode)
- [ ] Regime-Change-Szenario durchgespielt
- [ ] SBuMT-Korrektur für Anzahl getesteter Varianten
- [ ] Alpha-Quelle ökonomisch erklärbar (nicht nur statistisch)
- [ ] Lifecycle-Phase identifiziert (neu / reif / decaying)
- [ ] → Übergabe an riskOwner mit: Typ, SR, Skew, Turnover, Regime-Risiken
- [ ] → Übergabe an executionBroker mit: Frequenz, Instrumente, Signalstruktur

---

## Referenzen

Lies `references/insights.md` für vollständige Quell-Passagen.

Relevante Insights: 1-11, 16-17, 19-22, 27-31, 34, 37, 41-42, 46, 50, 59, 61, 69, 80, 82-83, 99-100.
