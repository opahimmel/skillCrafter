# Fragenkatalog: SiencTrading — Run 5 (Lückenschluss — Final)

## Adaptive Robust Execution — Quantitative Bedingungen

- What is the formal condition in terms of the signal-to-noise ratio of drift estimation that determines whether the adaptive robust strategy outperforms the fixed-interval robust strategy?
- How does the size of the uncertainty interval shrink over the trading window in the adaptive robust model and what determines the convergence rate?
- What happens to the adaptive robust strategy when the prior distribution of the drift is misspecified — does it converge to the correct estimate?

## FX Triplet — Statistische Arbitrage Formale Struktur

- How is the statistical spread of the FX triplet formally defined and estimated, and what is the mean-reversion half-life of this spread?
- What is the formal cointegration structure between the three FX pairs and how does the strategy exploit deviations from this long-run relationship?
- What are the specific performance metrics (Sharpe, PnL, drawdown) for the RDMM FX triplet strategy versus the DDQN strategy in backtesting?

## HAR-DRD Dekomposition — Kovarianz-Modellierung

- What is the specific DRD (Diagonal-Rotation-Diagonal) decomposition of the realized covariance matrix and how does it separate volatilities from correlations?
- How does the GHAR model aggregate neighborhood information from the asset graph, and what is the specific form of the GHAR regression equation?
- What is the in-sample R-squared improvement from adding graph predictors to the HAR-DRD baseline and how does it differ for volatility vs correlation sub-tasks?

## Deep Momentum Network — Architektur und Lernmechanismus

- What is the specific LSTM architecture in Deep Momentum Networks and how does it simultaneously learn trend direction and position size in a single forward pass?
- How does the Sharpe ratio optimization in DMN backpropagation differ from standard cross-entropy loss, and what gradient approximation is used?
- What is the specific performance gap between DMN-LSTM and traditional TSMOM/MACD strategies across the 2003-2020 period?

## Price-Trigger Koordination — AI Kollusion vollständig verstehen

- What is the exact structure of the price-trigger strategy characterized by the triple (η, ω, T) and how does it implement implicit coordination among AI speculators?
- Under what formal condition on noise trading σu does the price-trigger strategy fail to sustain a collusive Nash equilibrium?
- How do AI speculators learn to coordinate without explicit communication — what is the specific learning dynamic that leads to the price-trigger equilibrium?

## DeFi/CFM — Pool-Modell und Breakdown-Bedingungen

- What is the specific constant pool depth κ assumption in the CFM liquidation model and under what conditions does it fail in practice for Uniswap v3?
- How does the optimal liquidation strategy in a CFM differ between the case where rate formation is in the CEX vs the case where rate formation is in the DEX?

## Network Momentum — Out-of-Sample Validierung

- What is the full out-of-sample backtesting setup for the network momentum strategy — time period, assets, benchmark, and statistical test used?
- How does the network momentum strategy perform across asset classes (commodities, equities, bonds, FX) and which asset class shows the strongest and weakest signal?
- What is the Sharpe ratio improvement from network momentum over individual momentum strategies across different cost assumptions?
