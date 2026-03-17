# Skill: VWAP Mean Reversion Strategy
# Collection: trading_bot_skills
# Skill-ID: vwap_mr
# Version: 3.0 – English, B+C variants only
# Threshold: 0.70
#
# Rationale for English:
#   All source books are written in English. nomic-embed-text-v1.5 is multilingual
#   but cross-language similarity loses ~5-10% score. English queries → higher scores.
#
# Rationale for B+C only (dropping A):
#   v3 analysis showed A (technical) mostly produces false positives at threshold 0.68.
#   B (conceptual, short, no jargon) and C (narrative, first-person) consistently
#   outperform A. C opened the most new matches.
#
# Writing style guide for these queries:
#   B: Short, universal, sounds like a chapter title or section heading in a trading book.
#      No ticker names, no percentages, no technical jargon.
#   C: First-person confession or question. Sounds like a trader talking to a mentor,
#      or the opening anecdote of a book chapter. Use "I have been", "I noticed", "my strategy".

---

## MR-Q01-B

**query:** "When does mean reversion stop working and what tells you the market has changed?"

```yaml
id: MR-Q01-B
skill: vwap_mr
category: strategy
concept_anchor: vwap_mean_reversion_edge_validity
variant: conceptual_en
```

## MR-Q01-C

**query:** "I run a mean reversion strategy on individual stocks intraday. Some days it works perfectly, other days it loses consistently. How do I know whether the market is in a mean-reverting regime or not, and should I just stop trading on the bad days?"

```yaml
id: MR-Q01-C
skill: vwap_mr
category: strategy
concept_anchor: vwap_mean_reversion_edge_validity
variant: narrative_en
```

---

## MR-Q02-B

**query:** "How far does a price need to deviate from its average before a trade makes sense?"

```yaml
id: MR-Q02-B
skill: vwap_mr
category: strategy
concept_anchor: entry_band_calibration_vwap
variant: conceptual_en
```

## MR-Q02-C

**query:** "My strategy buys when price drops below a reference level. Sometimes these are small dips that snap back immediately, sometimes the stock keeps falling. How do I find the right entry threshold that captures real reversions and avoids catching falling knives?"

```yaml
id: MR-Q02-C
skill: vwap_mr
category: strategy
concept_anchor: entry_band_calibration_vwap
variant: narrative_en
```

---

## MR-Q03-B

**query:** "How often does a trade need to win to be profitable when winners are bigger than losers?"

```yaml
id: MR-Q03-B
skill: vwap_mr
category: risk
concept_anchor: risk_reward_breakeven_winrate
variant: conceptual_en
```

## MR-Q03-C

**query:** "I lose more often than I win but my winning trades are larger than my losing trades. Is that enough to be profitable in the long run, and how sensitive is the whole thing to a small drop in win rate?"

```yaml
id: MR-Q03-C
skill: vwap_mr
category: risk
concept_anchor: risk_reward_breakeven_winrate
variant: narrative_en
```

---

## MR-Q04-B

**query:** "When does a stop loss hurt a mean reversion strategy more than it helps?"

```yaml
id: MR-Q04-B
skill: vwap_mr
category: risk
concept_anchor: stop_loss_noise_calibration
variant: conceptual_en
```

## MR-Q04-C

**query:** "My stop loss keeps getting triggered and then the price immediately reverses back in my direction. The stop is not protecting me — it is costing me money on every trade. What am I doing wrong and how should I set the stop correctly for a mean reversion strategy?"

```yaml
id: MR-Q04-C
skill: vwap_mr
category: risk
concept_anchor: stop_loss_noise_calibration
variant: narrative_en
```

---

## MR-Q05-B

**query:** "How do you avoid fooling yourself when testing whether a filter improves a strategy?"

```yaml
id: MR-Q05-B
skill: vwap_mr
category: regime
concept_anchor: trend_filter_sma_length_optimization
variant: conceptual_en
```

## MR-Q05-C

**query:** "I have been tweaking my backtest for weeks and every change I make improves the results. But now I am worried that the strategy only looks good because I have fitted it to past data. How do I know whether the improvements are real or whether I am just overfitting?"

```yaml
id: MR-Q05-C
skill: vwap_mr
category: regime
concept_anchor: trend_filter_sma_length_optimization
variant: narrative_en
```

---

## MR-Q06-B

**query:** "In which market conditions should you stop trading a mean reversion strategy?"

```yaml
id: MR-Q06-B
skill: vwap_mr
category: regime
concept_anchor: market_regime_filter_vix_spy
variant: conceptual_en
```

## MR-Q06-C

**query:** "My mean reversion strategy works well in calm markets but bleeds money whenever there is a crash or a period of high volatility. How do I detect these dangerous regimes in advance and pause my bot before the losses accumulate?"

```yaml
id: MR-Q06-C
skill: vwap_mr
category: regime
concept_anchor: market_regime_filter_vix_spy
variant: narrative_en
```

---

## MR-Q07-B

**query:** "How do you honestly test whether a trading strategy works and is not just a lucky fit to historical data?"

```yaml
id: MR-Q07-B
skill: vwap_mr
category: backtest
concept_anchor: walk_forward_validation_methodology
variant: conceptual_en
```

## MR-Q07-C

**query:** "My backtest looks excellent. But I have no idea whether to trust it or whether it is just fitting noise in my historical data. What would convince me that the edge is real and not an artifact of how I tested the strategy?"

```yaml
id: MR-Q07-C
skill: vwap_mr
category: backtest
concept_anchor: walk_forward_validation_methodology
variant: narrative_en
```

---

## MR-Q08-B

**query:** "Why do most traders perform worse live than their backtest predicted?"

```yaml
id: MR-Q08-B
skill: vwap_mr
category: backtest
concept_anchor: slippage_cost_assumptions_realism
variant: conceptual_en
```

## MR-Q08-C

**query:** "My backtest is profitable but I am losing money in live trading. The only explanation I can think of is that my actual fill prices are worse than what the backtest assumed. How large is this effect typically, and how should I model transaction costs more realistically?"

```yaml
id: MR-Q08-C
skill: vwap_mr
category: backtest
concept_anchor: slippage_cost_assumptions_realism
variant: narrative_en
```

---

## MR-Q09-B

**query:** "At what Sharpe ratio should you become suspicious that a backtest result is too good to be true?"

```yaml
id: MR-Q09-B
skill: vwap_mr
category: backtest
concept_anchor: overfitting_diagnosis_backtest_period
variant: conceptual_en
```

## MR-Q09-C

**query:** "My backtest shows a Sharpe ratio of almost 3.0 on a single stock ticker over six months. My colleague says that is too good to be real and I must have overfit the strategy. Is he right, and how do I tell whether my results reflect genuine edge or just overfitting?"

```yaml
id: MR-Q09-C
skill: vwap_mr
category: backtest
concept_anchor: overfitting_diagnosis_backtest_period
variant: narrative_en
```

---

## MR-Q10-B

**query:** "Is it better to specialize in a few instruments or trade many simultaneously?"

```yaml
id: MR-Q10-B
skill: vwap_mr
category: universe
concept_anchor: universe_size_position_diversification
variant: conceptual_en
```

## MR-Q10-C

**query:** "I trade sixteen different stocks simultaneously and thought I was well diversified. But whenever the market sells off, all my positions lose money at the same time. Do I have a diversification problem and how do I fix it?"

```yaml
id: MR-Q10-C
skill: vwap_mr
category: universe
concept_anchor: universe_size_position_diversification
variant: narrative_en
```

---

## MR-Q11-B

**query:** "Does an ETF behave differently intraday than the individual stocks it contains?"

```yaml
id: MR-Q11-B
skill: vwap_mr
category: universe
concept_anchor: spy_etf_vwap_mean_reversion_suitability
variant: conceptual_en
```

## MR-Q11-C

**query:** "I included SPY in my universe because it is very liquid. But SPY moves differently from my individual stock positions — it seems to have less idiosyncratic noise. Should I trade SPY the same way I trade single stocks, or does it need a different approach?"

```yaml
id: MR-Q11-C
skill: vwap_mr
category: universe
concept_anchor: spy_etf_vwap_mean_reversion_suitability
variant: narrative_en
```

---

## MR-Q12-B

**query:** "Why is the first half hour after market open dangerous for intraday strategies?"

```yaml
id: MR-Q12-B
skill: vwap_mr
category: timing
concept_anchor: opening_skip_calibration
variant: conceptual_en
```

## MR-Q12-C

**query:** "I start trading at exactly 09:30 but my worst trades always happen in the first few minutes after the open. After that my performance improves significantly. Should I just skip the opening period entirely, and if so how many minutes should I wait?"

```yaml
id: MR-Q12-C
skill: vwap_mr
category: timing
concept_anchor: opening_skip_calibration
variant: narrative_en
```

---

## MR-Q13-B

**query:** "What is the best way to close positions at end of day with minimal slippage?"

```yaml
id: MR-Q13-B
skill: vwap_mr
category: timing
concept_anchor: eod_close_slippage_market_orders
variant: conceptual_en
```

## MR-Q13-C

**query:** "I need to close all my positions before the market closes every day. When I use market orders I get poor fills. Is there a better order type I should use, and does it matter whether I send the orders fifteen minutes before close or right at the close?"

```yaml
id: MR-Q13-C
skill: vwap_mr
category: timing
concept_anchor: eod_close_slippage_market_orders
variant: narrative_en
```

---

## MR-Q14-B

**query:** "How long do you need to observe a strategy before trusting it with real money?"

```yaml
id: MR-Q14-B
skill: vwap_mr
category: roadmap
concept_anchor: paper_trading_duration_validation
variant: conceptual_en
```

## MR-Q14-C

**query:** "My backtest convinces me. I want to go live. But I am afraid the backtest is misleading me. How long should I paper trade, and what specific numbers need to check out before I risk real capital?"

```yaml
id: MR-Q14-C
skill: vwap_mr
category: roadmap
concept_anchor: paper_trading_duration_validation
variant: narrative_en
```

---

## MR-Q15-B

**query:** "When does adding machine learning to a trading strategy make it better, and when does it make it worse?"

```yaml
id: MR-Q15-B
skill: vwap_mr
category: roadmap
concept_anchor: ml_filter_phase2_timing_requirements
variant: conceptual_en
```

## MR-Q15-C

**query:** "My rule-based strategy works well. I want to add a machine learning filter to remove bad trades. But I am worried the ML model will block the good trades and only learn noise from my limited data. How do I approach this correctly without destroying the edge I already have?"

```yaml
id: MR-Q15-C
skill: vwap_mr
category: roadmap
concept_anchor: ml_filter_phase2_timing_requirements
variant: narrative_en
```

---

## MR-Q16-B

**query:** "Is it better to react to market events as they happen or to poll prices at regular intervals?"

```yaml
id: MR-Q16-B
skill: vwap_mr
category: arch
concept_anchor: polling_vs_eventdriven_ibkr_data
variant: conceptual_en
```

## MR-Q16-C

**query:** "My trading bot checks for new prices every minute. A friend says I should use callbacks so the program reacts immediately when a new bar arrives instead of polling on a schedule. What is the practical difference for a one-minute bar strategy and is it worth the effort to rewrite?"

```yaml
id: MR-Q16-C
skill: vwap_mr
category: arch
concept_anchor: polling_vs_eventdriven_ibkr_data
variant: narrative_en
```

---

## Metadaten

```yaml
catalog: skill_vwap_mr
version: "3.0"
language: en
total_questions: 32
variants_per_topic: 2   # B (conceptual) + C (narrative) only — A dropped
threshold: 0.70
model: nomic-ai/nomic-embed-text-v1.5
rationale_english: "Source books are in English — same-language queries score ~5-10% higher"
rationale_bc_only: "v3 analysis: A produces false positives, B+C open genuine matches"
best_performing_variant: "C (narrative) — opens most new matches, matches book anecdote style"
```
