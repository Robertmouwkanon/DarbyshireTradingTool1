import os
import time
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# =========================
# Translations (nl / en)
# =========================
def _tr() -> dict:
    return {
        "disclaimer": {"nl": "⚠️ For research/education. Not financial advice.", "en": "⚠️ For research/education. Not financial advice."},
        "menu": {"nl": "Menu", "en": "Menu"},
        "choose": {"nl": "Kies", "en": "Choose"},
        "page_home": {"nl": "Home", "en": "Home"},
        "page_koersdata": {"nl": "Koersdata", "en": "Price data"},
        "page_signals": {"nl": "Signals", "en": "Signals"},
        "page_gold": {"nl": "Koopsignalen Gold", "en": "Buy signals Gold"},
        "page_sp500": {"nl": "S&P 500", "en": "S&P 500"},
        "page_backtest": {"nl": "Backtest", "en": "Backtest"},
        "page_export": {"nl": "Export (later)", "en": "Export (later)"},
        "us_ticker": {"nl": "US ticker", "en": "US ticker"},
        "us_ticker_help": {"nl": "De beurscode van het aandeel of fonds (bijv. AAPL = Apple, GLD = goud-ETF). Alleen US-tickers.", "en": "Stock or fund symbol (e.g. AAPL = Apple, GLD = gold ETF). US tickers only."},
        "days_data": {"nl": "Aantal dagen data", "en": "Days of data"},
        "days_data_help": {"nl": "Hoeveel dagen koersgeschiedenis wordt meegenomen. Meer dagen = langere backtest, maar oudere data weegt mee.", "en": "How many days of price history to use. More days = longer backtest, older data included."},
        "signal_settings": {"nl": "Signal instellingen", "en": "Signal settings"},
        "rsi_period": {"nl": "RSI periode", "en": "RSI period"},
        "rsi_period_help": {"nl": "RSI meet of iets 'oververhit' of 'oversold' is. Hogere periode = rustiger signaal, lagere = gevoeliger.", "en": "RSI measures overbought/oversold. Higher period = smoother signal, lower = more sensitive."},
        "buy_threshold_help": {"nl": "Vanaf welke confidence (0–1) het model BUY geeft. Hoger = strenger (minder vaak koop), lager = vaker koop.", "en": "Above this confidence (0–1) the model gives BUY. Higher = stricter, lower = more buy signals."},
        "backtest_settings": {"nl": "Backtest instellingen", "en": "Backtest settings"},
        "exit_threshold_help": {"nl": "Onder welke confidence we uit een positie stappen. Lager = langer vasthouden, hoger = sneller verkopen.", "en": "Below this confidence we exit. Lower = hold longer, higher = exit sooner."},
        "max_hold_help": {"nl": "Maximaal aantal dagen in een trade; daarna wordt automatisch gesloten (ongeacht winst/verlies).", "en": "Max days in a trade; then position is closed automatically (regardless of P&L)."},
        "conf_buckets": {"nl": "D: Confidence buckets", "en": "D: Confidence buckets"},
        "buckets_caption": {"nl": "Buckets bepalen hoe we performance groeperen.", "en": "Buckets define how we group performance."},
        "bucket1_help": {"nl": "Einde van de laagste confidence-groep (bijv. 0.60 = alles van 0 tot 0.60 in bucket 1).", "en": "End of lowest confidence group (e.g. 0.60 = all from 0 to 0.60 in bucket 1)."},
        "bucket2_help": {"nl": "Einde van bucket 2. Moet groter zijn dan bucket 1.", "en": "End of bucket 2. Must be greater than bucket 1."},
        "bucket3_help": {"nl": "Einde van bucket 3. Alles daarboven tot 1.00 zit in de hoogste bucket.", "en": "End of bucket 3. Everything above up to 1.00 is in the highest bucket."},
        "buy_criterion_label": {"nl": "Koopsignaal criterium", "en": "Buy signal criterion"},
        "buy_criterion_confidence": {"nl": "Confidence (standaard)", "en": "Confidence (default)"},
        "buy_criterion_4pct": {"nl": "Kans op 4% winst in 20 dagen", "en": "Chance of 4% profit in 20 days"},
        "min_prob_4pct_label": {"nl": "Min. kans op 4% (%)", "en": "Min. chance of 4% (%)"},
        "min_prob_4pct_help": {"nl": "BUY alleen als historisch bij deze setup+bucket minstens deze % van de trades (binnen 20 dagen) 4%+ winst maakte.", "en": "BUY only if historically for this setup+bucket at least this % of trades (within 20 days) made 4%+ profit."},
        "signal_basis_explanation": {"nl": "In de basis: BUY wanneer confidence ≥ drempel (RSI + trend + momentum).", "en": "By default: BUY when confidence ≥ threshold (RSI + trend + momentum)."},
        "signal_4pct_explanation": {"nl": "Je kiest nu: BUY wanneer de historische kans op 4% winst binnen 20 dagen ≥ {pct:.0f}% (bij deze setup+bucket).", "en": "You chose: BUY when historical chance of 4% profit within 20 days ≥ {pct:.0f}% (for this setup+bucket)."},
        "kans_4pct_label": {"nl": "Kans op 4% in 20d (historisch)", "en": "Chance of 4% in 20d (historical)"},
        "geen_data_4pct": {"nl": "Geen historische data voor 4%-regel bij deze setup+bucket.", "en": "No historical data for 4% rule for this setup+bucket."},
        # Risk & position sizing
        "risk_sidebar_title": {"nl": "Risk / positie–grootte", "en": "Risk / position sizing"},
        "account_size_label": {"nl": "Accountgrootte (USD)", "en": "Account size (USD)"},
        "account_size_help": {"nl": "Totaal vermogen waarop je je risico per trade baseert.", "en": "Total capital you base per-trade risk on."},
        "max_risk_pct_label": {"nl": "Max risico per trade (%)", "en": "Max risk per trade (%)"},
        "max_risk_pct_help": {"nl": "Welk deel van je account je maximaal wilt riskeren op één trade (bijv. 1%).", "en": "Which share of your account you are willing to risk on a single trade (e.g. 1%)."},
        "stop_pct_label": {"nl": "Stop-afstand onder huidige koers (%)", "en": "Stop distance below current price (%)"},
        "stop_pct_help": {"nl": "Hoeveel % onder de huidige koers je ongeveer je stop-loss zou leggen.", "en": "How many % below current price you would roughly place your stop-loss."},
        "risk_block_title": {"nl": "Maximale positie (op basis van risico)", "en": "Maximum position (based on risk)"},
        "risk_summary": {"nl": "Met een account van **${account:,.0f}** en max risico **{risk_pct:.1f}%** en een stop **{stop_pct:.1f}%** onder de huidige koers (~${price:.2f}) kun je maximaal **{shares} stuks** kopen van **{ticker}** (ongeveer **${exposure:,.0f}** positie) met een risicobedrag rond **${risk_amount:,.0f}**.", "en": "With an account of **${account:,.0f}** and max risk **{risk_pct:.1f}%** and a stop **{stop_pct:.1f}%** below the current price (~${price:.2f}), you can buy at most **{shares} shares** of **{ticker}** (about **${exposure:,.0f}** position) with risk around **${risk_amount:,.0f}**."},
        "risk_too_small": {"nl": "Met deze instellingen is het risicobedrag kleiner dan het verlies per aandeel; verlaag de stop-afstand of verhoog het max risico–%.", "en": "With these settings the total risk is smaller than the loss per share; reduce stop distance or increase max risk %."},
        # Watchlist
        "watchlist_title": {"nl": "Watchlist (snelle keuze)", "en": "Watchlist (quick select)"},
        "watchlist_help": {"nl": "Klik op een ticker om het veld 'US ticker' direct in te vullen.", "en": "Click a ticker to fill the 'US ticker' field directly."},
        "page_watchlist": {"nl": "Watchlist", "en": "Watchlist"},
        "watchlist_page_title": {"nl": "Watchlist — overzicht", "en": "Watchlist — overview"},
        "watchlist_page_intro": {"nl": "Overzicht van je vaste tickers met het huidige signaal, confidence en historische kans ≥4% in 20 dagen.", "en": "Overview of your watchlist tickers with current signal, confidence and historical chance ≥4% in 20 days."},
        "watchlist_empty": {"nl": "Geen watchlist‑tickers konden worden geladen (controleer internet/API‑limieten).", "en": "No watchlist tickers could be loaded (check internet/API limits)."},
        # Optimizer
        "page_optimizer": {"nl": "Optimizer", "en": "Optimizer"},
        "optimizer_title": {"nl": "Optimizer — parameter scan", "en": "Optimizer — parameter scan"},
        "optimizer_intro": {"nl": "Voor de huidige ticker wordt een klein raster van instellingen getest (BUY‑drempel, EXIT‑drempel, Max hold days). Voor elke combinatie zie je totale backtest‑return, max drawdown, winrate en kans ≥4% in 20 dagen.", "en": "For the current ticker a small grid of settings is tested (BUY threshold, EXIT threshold, Max hold days). For each combination you see total backtest return, max drawdown, win rate and chance ≥4% in 20 days."},
        "optimizer_run_button": {"nl": "Run optimizer voor huidige ticker", "en": "Run optimizer for current ticker"},
        "optimizer_no_results": {"nl": "Geen resultaten (mogelijk geen trades voor deze combinaties).", "en": "No results (possibly no trades for these combinations)."},
        "debug": {"nl": "🔧 Debug", "en": "🔧 Debug"},
        "api_key_present": {"nl": "API key aanwezig:", "en": "API key present:"},
        # Home
        "home_title": {"nl": "Waar staan we?", "en": "Where we are"},
        "home_bullet1": {"nl": "✅ Koersdata terug in menu.", "en": "✅ Price data in menu."},
        "home_bullet2": {"nl": "✅ Signals: live + historische verwachting bij dezelfde setup/bucket.", "en": "✅ Signals: live + historical expectation for same setup/bucket."},
        "home_bullet3": {"nl": "✅ Backtest: equity + drawdown + trades + conditional stats.", "en": "✅ Backtest: equity + drawdown + trades + conditional stats."},
        "home_expander": {"nl": "ℹ️ Uitleg voor beginners", "en": "ℹ️ Explanation for beginners"},
        "home_expander_text": {"nl": "**Darbyshire Trading Tool** gebruikt koersdata en technische indicatoren om een **koopsignaal** (BUY of HOLD) te geven. Dat is geen garantie: het is een hulpmiddel voor onderzoek. **Confidence** (0–1) is een score die RSI, trend en momentum combineert; boven de drempel krijg je BUY. **Backtest** laat zien hoe het signaal in het verleden had uitgepakt.", "en": "**Darbyshire Trading Tool** uses price data and technical indicators to give a **buy signal** (BUY or HOLD). Not a guarantee—for research only. **Confidence** (0–1) combines RSI, trend and momentum; above the threshold you get BUY. **Backtest** shows how the signal would have performed in the past."},
        # Koersdata
        "koersdata_cols_title": {"nl": "ℹ️ Wat betekenen de kolommen?", "en": "ℹ️ What do the columns mean?"},
        "koersdata_cols_text": {"nl": "- **open/high/low/close**: koers op de dag (open = start, close = slot).\n- **volume**: aantal verhandelde stuks.\n- **rsi**: Relative Strength Index (0–100); onder 30 vaak 'oversold', boven 70 'overbought'.\n- **ema20/50/200**: gemiddelde koers over 20, 50 of 200 dagen (trend).\n- **roc10**: procentuele verandering over 10 dagen (momentum).\n- **range_pct**: spreiding hoog–laag (volatiliteit).\n- **confidence**: model-score 0–1; hoger = sterker signaal.\n- **conf_bucket**: confidence in een groep (voor statistiek).\n- **setup**: type marktsituatie (Bird = dip, Green = trend, Grey = onduidelijk, None).\n- **signal**: BUY of HOLD op basis van de drempel.", "en": "- **open/high/low/close**: daily price (open = start, close = end).\n- **volume**: number of shares/funds traded.\n- **rsi**: Relative Strength Index (0–100); below 30 often oversold, above 70 overbought.\n- **ema20/50/200**: average price over 20, 50 or 200 days (trend).\n- **roc10**: % change over 10 days (momentum).\n- **range_pct**: high–low spread (volatility).\n- **confidence**: model score 0–1; higher = stronger signal.\n- **conf_bucket**: confidence group (for stats).\n- **setup**: market type (Bird = dip, Green = trend, Grey = unclear, None).\n- **signal**: BUY or HOLD based on threshold."},
        "chart_close": {"nl": "Koersgrafiek (Close)", "en": "Price chart (Close)"},
        "error_koersdata": {"nl": "Fout bij Koersdata:", "en": "Error loading price data:"},
        # Signals
        "signals_expander": {"nl": "ℹ️ Uitleg begrippen", "en": "ℹ️ Glossary"},
        "signals_expander_text": {"nl": "- **Signal**: aanbeveling van het model: **BUY** (koop) of **HOLD** (wacht).\n- **Confidence**: score van 0 tot 1; hoe hoger, hoe sterker het model het signaal vindt. Boven je BUY-drempel → BUY.\n- **RSI**: Relative Strength Index; onder 30 vaak oversold, boven 70 overbought.\n- **Setup**: type situatie — *Bird* = dip/herstel, *Green* = opwaartse trend, *Grey* = onduidelijk, *None* = geen van deze.\n- **Bucket**: welk confidence-bereik (bijv. 0.65–0.70); gebruikt om historische resultaten te vergelijken.\n- **Historische verwachting**: hoe trades met dezelfde setup+bucket in het verleden presteerden (geen garantie voor de toekomst).", "en": "- **Signal**: model recommendation **BUY** (buy) or **HOLD** (wait).\n- **Confidence**: score 0–1; higher = stronger signal. Above your BUY threshold → BUY.\n- **RSI**: Relative Strength Index; below 30 often oversold, above 70 overbought.\n- **Setup**: situation type — *Bird* = dip/recovery, *Green* = uptrend, *Grey* = unclear, *None* = none.\n- **Bucket**: confidence range (e.g. 0.65–0.70); used to compare historical results.\n- **Historical expectation**: how trades with same setup+bucket performed in the past (no guarantee for future)."},
        "signal_help": {"nl": "BUY = koop, HOLD = wacht.", "en": "BUY = buy, HOLD = wait."},
        "confidence_help": {"nl": "Score 0–1; boven de drempel → BUY.", "en": "Score 0–1; above threshold → BUY."},
        "rsi_help": {"nl": "Onder 30 vaak oversold, boven 70 overbought.", "en": "Below 30 often oversold, above 70 overbought."},
        "setup_help": {"nl": "Bird = dip, Green = trend, Grey = onduidelijk.", "en": "Bird = dip, Green = trend, Grey = unclear."},
        "bucket_help": {"nl": "Confidence-bereik voor vergelijking met verleden.", "en": "Confidence range for comparison with history."},
        "live_caption": {"nl": "Live context (Signals): dit is wat je NU ziet. Voor uitleg van de termen: klap 'Uitleg begrippen' hierboven open.", "en": "Live context: this is what you see now. For term definitions, expand 'Glossary' above."},
        "hist_exp_title": {"nl": "Historische verwachting bij dit signaal", "en": "Historical expectation for this signal"},
        "no_trades_warn": {"nl": "Nog geen trades -> geen historische verwachting. Verlaag BUY threshold of vergroot days.", "en": "No trades yet → no historical expectation. Lower BUY threshold or increase days."},
        "no_hist_trades": {"nl": "Geen historische trades voor exact deze setup/bucket (nog).", "en": "No historical trades for this exact setup/bucket yet."},
        "median_month": {"nl": "Median maand (P50)", "en": "Median month (P50)"},
        "median_month_help": {"nl": "Typisch resultaat: de middelste maandopbrengst in het verleden bij deze setup.", "en": "Typical result: the median monthly return in the past for this setup."},
        "prob_pos_month": {"nl": "Kans op positieve maand", "en": "Probability positive month"},
        "prob_pos_help": {"nl": "Hoe vaak was de maandopbrengst positief? (historisch)", "en": "How often was the monthly return positive? (historical)"},
        "p05_label": {"nl": "Slecht scenario (P05)", "en": "Worst scenario (P05)"},
        "p05_help": {"nl": "Alleen 5% van de maanden was slechter dan dit; een ruwe ondergrens.", "en": "Only 5% of months were worse; a rough lower bound."},
        "n_trades": {"nl": "Aantal trades", "en": "Number of trades"},
        "n_trades_help": {"nl": "Aantal historische trades in deze setup+bucket.", "en": "Number of historical trades in this setup+bucket."},
        "prob_4pct_20d_label": {"nl": "Kans ≥4% in 20d", "en": "Chance ≥4% in 20d"},
        "prob_4pct_20d_help": {"nl": "Historische kans dat een trade binnen 20 dagen minstens 4% winst maakt bij deze setup+bucket.", "en": "Historical chance that a trade within 20 days makes at least 4% profit for this setup+bucket."},
        "trade_card_title": {"nl": "Historische kans bij dit signaal", "en": "Historical odds for this signal"},
        "trade_card_no_data": {"nl": "Nog geen historische trades voor deze setup/bucket.", "en": "No historical trades yet for this setup/bucket."},
        # Marktfilter
        "market_filter_label": {"nl": "Marktfilter (S&P 500)", "en": "Market filter (S&P 500)"},
        "market_filter_help": {"nl": "Als dit aan staat, wordt een BUY alleen toegestaan als de S&P 500 (SPY) zelf ook een BUY‑signaal heeft én de langere trend (EMA50 > EMA200) opwaarts is.", "en": "When enabled, BUY is only allowed if the S&P 500 (SPY) itself has a BUY signal and the longer trend (EMA50 > EMA200) is up."},
        "market_filter_ok": {"nl": "Marktfilter actief: S&P 500 ziet er positief uit (BUY en opwaartse trend).", "en": "Market filter active: S&P 500 looks positive (BUY and uptrend)."},
        "market_filter_blocked": {"nl": "Marktfilter actief: S&P 500 is niet positief genoeg; BUY‑signaal voor deze ticker wordt gedempt naar HOLD.", "en": "Market filter active: S&P 500 is not sufficiently positive; BUY signal for this ticker is downgraded to HOLD."},
        "conditional_caption": {"nl": "Conditioneel (zelfde setup + bucket als vandaag). Percentielen zijn gebaseerd op maand-samples (som trade returns per entry-maand).", "en": "Conditional (same setup + bucket as today). Percentiles based on monthly samples (sum of trade returns per entry month)."},
        "few_samples": {"nl": "Te weinig maand-samples voor stabiele P05/P50. Hieronder wel trade-level statistieken.", "en": "Too few monthly samples for stable P05/P50. Trade-level stats below."},
        "winrate": {"nl": "Winrate (trades)", "en": "Win rate (trades)"},
        "winrate_help": {"nl": "Percentage trades met winst in het verleden bij deze setup.", "en": "Share of trades that were profitable in the past for this setup."},
        "expectancy": {"nl": "Expectancy / trade", "en": "Expectancy per trade"},
        "expectancy_help": {"nl": "Verwachte opbrengst per trade (winrate × gem. winst − verliesrate × gem. verlies).", "en": "Expected return per trade (win rate × avg win − loss rate × avg loss)."},
        "median_trade": {"nl": "Median trade", "en": "Median trade"},
        "median_trade_help": {"nl": "De middelste trade-opbrengst (niet het gemiddelde).", "en": "The median trade return (not the average)."},
        "avg_hold": {"nl": "Gem. hold (dagen)", "en": "Avg hold (days)"},
        "avg_hold_help": {"nl": "Gemiddeld aantal dagen in een trade bij deze setup.", "en": "Average days in a trade for this setup."},
        "overview_d": {"nl": "Overzicht (alle setups/buckets)", "en": "Overview (all setups/buckets)"},
        "conditional_stats_exp": {"nl": "ℹ️ Wat zijn conditional stats?", "en": "ℹ️ What are conditional stats?"},
        "conditional_stats_text": {"nl": "Hier zie je per **setup** (Bird/Green/Grey/None) en **bucket** (confidence-bereik) hoe trades in het verleden presteerden: **winrate**, **expectancy**, **profit factor**. Zo kun je zien bij welke combinaties het model historisch beter scoorde. Geen garantie voor de toekomst.", "en": "Per **setup** (Bird/Green/Grey/None) and **bucket** (confidence range) you see how past trades performed: **win rate**, **expectancy**, **profit factor**. So you can see which combinations historically did better. No guarantee for the future."},
        "no_conditional": {"nl": "Nog geen conditional stats (geen trades).", "en": "No conditional stats yet (no trades)."},
        "error_signals": {"nl": "Fout bij Signals:", "en": "Error on Signals:"},
        # Optimizer
        "page_optimizer": {"nl": "Optimizer", "en": "Optimizer"},
        "optimizer_title": {"nl": "Optimizer — parameter scan", "en": "Optimizer — parameter scan"},
        "optimizer_intro": {"nl": "Voor de huidige ticker wordt een klein raster van instellingen getest (BUY‑drempel, EXIT‑drempel, Max hold days). Voor elke combinatie zie je totale backtest‑return, max drawdown, winrate en kans ≥4% in 20 dagen.", "en": "For the current ticker a small grid of settings is tested (BUY threshold, EXIT threshold, Max hold days). For each combination you see total backtest return, max drawdown, win rate and chance ≥4% in 20 days."},
        "optimizer_run_button": {"nl": "Run optimizer voor huidige ticker", "en": "Run optimizer for current ticker"},
        "optimizer_no_results": {"nl": "Geen resultaten (mogelijk geen trades voor deze combinaties).", "en": "No results (possibly no trades for these combinations)."},
        "optimizer_best_summary": {"nl": "Beste combinatie: BUY‑drempel **{buy_th:.2f}**, EXIT‑drempel **{exit_th:.2f}**, Max hold **{max_hold}** dagen → totale return **{total_return:.1%}**, max drawdown **{max_drawdown:.1%}**, winrate **{winrate:.1%}**, kans ≥4% in 20d **{prob4}**, trades **{trades}**.", "en": "Best combination: BUY threshold **{buy_th:.2f}**, EXIT threshold **{exit_th:.2f}**, Max hold **{max_hold}** days → total return **{total_return:.1%}**, max drawdown **{max_drawdown:.1%}**, win rate **{winrate:.1%}**, chance ≥4% in 20d **{prob4}**, trades **{trades}**."},
        "optimizer_vs_current": {"nl": "Huidig: BUY‑drempel **{cur_buy:.2f}**, EXIT‑drempel **{cur_exit:.2f}**, Max hold **{cur_hold}** dagen.", "en": "Current: BUY threshold **{cur_buy:.2f}**, EXIT threshold **{cur_exit:.2f}**, Max hold **{cur_hold}** days."},
        # Signals — Analyse & Koopsignaal summary
        "summary_buy_box": {"nl": "🟢 **Koopsignaal: BUY** — Het model geeft een koopsignaal op basis van de huidige indicatoren.", "en": "🟢 **Buy signal: BUY** — The model gives a buy signal based on current indicators."},
        "summary_hold_box": {"nl": "🟠 **Koopsignaal: HOLD** — Geen koopsignaal; wacht op betere omstandigheden.", "en": "🟠 **Buy signal: HOLD** — No buy signal; wait for better conditions."},
        "summary_expander": {"nl": "📋 Analyse & advies (uitklappen)", "en": "📋 Analysis & advice (expand)"},
        "summary_brief_analysis": {"nl": "**Korte analyse:**", "en": "**Brief analysis:**"},
        "summary_advice": {"nl": "Advies:", "en": "Advice:"},
        "recommended_title": {"nl": "Aanbevolen fonds (beste kans van slagen)", "en": "Recommended fund (best chance)"},
        "recommended_info": {"nl": "**Aanbevolen ticker: {ticker}** — Signaal: **{signal}**, confidence {conf:.2f}, RSI {rsi:.1f}, setup {setup}. Gebaseerd op de gekozen vergelijkingslijst; niet op historische backtest.", "en": "**Recommended ticker: {ticker}** — Signal: **{signal}**, confidence {conf:.2f}, RSI {rsi:.1f}, setup {setup}. Based on the comparison list; not on historical backtest."},
        "buy_recommendation": {"nl": "Aanbeveling: koop **{ticker}**", "en": "Recommendation: buy **{ticker}**"},
        "buy_recommendation_none": {"nl": "Aanbeveling: geen koop uit de vergelijkingslijst (geen van de tickers heeft nu een BUY-signaal).", "en": "Recommendation: no buy from the comparison list (none of the tickers has a BUY signal now)."},
        "compare_label": {"nl": "Tickers om te vergelijken (komma)", "en": "Tickers to compare (comma-separated)"},
        "compare_placeholder": {"nl": "SOXL, TQQQ, NVDA, SPY", "en": "SOXL, TQQQ, NVDA, SPY"},
        "compare_help": {"nl": "Laat leeg voor alleen de gekozen ticker. Vul in om het fonds met de beste kans te laten adviseren.", "en": "Leave empty for the selected ticker only. Fill in to get a recommended fund from the list."},
        "no_tickers_loaded": {"nl": "Geen van de opgegeven tickers kon worden geladen.", "en": "None of the given tickers could be loaded."},
        "loading_compare": {"nl": "Tickers vergelijken…", "en": "Comparing tickers…"},
        "compare_failed": {"nl": "Kon niet laden: ", "en": "Could not load: "},
        "compare_hint": {"nl": "Vul in de sidebar bij 'Aanbevolen fonds' tickers in (komma gescheiden, bijv. SOXL, TQQQ, NVDA) om hier een vergelijking te zien.", "en": "Enter tickers in the sidebar under 'Recommended fund' (comma-separated, e.g. SOXL, TQQQ, NVDA) to see a comparison here."},
        # S&P 500
        "sp500_title": {"nl": "S&P 500 — brede markt", "en": "S&P 500 — broad market"},
        "sp500_caption": {"nl": "Signalen en analyse voor de S&P 500 via SPY (ETF die de index volgt).", "en": "Signals and analysis for the S&P 500 via SPY (ETF tracking the index)."},
        "error_sp500": {"nl": "Fout bij S&P 500:", "en": "Error on S&P 500:"},
        # Configurator & prognose
        "configurator_title": {"nl": "Configurator (prognose)", "en": "Configurator (forecast)"},
        "day_move_label": {"nl": "Veronderstelde dagbeweging (%)", "en": "Assumed daily move (%)"},
        "day_move_help": {"nl": "Stel: slotkoers vandaag daalt of stijgt met dit percentage. Je ziet dan op Signals een prognose: zou het dan BUY zijn?", "en": "Assume today's close moves by this %. Signals page then shows a forecast: would it be BUY?"},
        "prognosis_title": {"nl": "Prognose bij veronderstelde dagbeweging", "en": "Forecast for assumed daily move"},
        "prognosis_down": {"nl": "Als de slotkoers vandaag **{pct}% daalt**, zou het signaal **{signal}** zijn (confidence {conf:.2f}, RSI {rsi:.1f}, setup {setup}).", "en": "If today's close **drops {pct}%**, the signal would be **{signal}** (confidence {conf:.2f}, RSI {rsi:.1f}, setup {setup})."},
        "prognosis_up": {"nl": "Als de slotkoers vandaag **{pct}% stijgt**, zou het signaal **{signal}** zijn (confidence {conf:.2f}, RSI {rsi:.1f}, setup {setup}).", "en": "If today's close **rises {pct}%**, the signal would be **{signal}** (confidence {conf:.2f}, RSI {rsi:.1f}, setup {setup})."},
        "prognosis_unchanged": {"nl": "Geen veronderstelde beweging (0%). Vul in de sidebar een percentage in voor een prognose.", "en": "No assumed move (0%). Enter a % in the sidebar for a forecast."},
        # Gold
        "gold_title": {"nl": "Koopsignalen Gold — Goud & Zilver", "en": "Buy signals Gold — Gold & Silver"},
        "gold_caption": {"nl": "Koopsignalen voor goud (GLD) en zilver (SLV) met dezelfde signalogica als op het Signals-tab.", "en": "Buy signals for gold (GLD) and silver (SLV) with the same signal logic as on the Signals tab."},
        "gold_expander": {"nl": "ℹ️ Uitleg", "en": "ℹ️ Explanation"},
        "gold_expander_text": {"nl": "**GLD** en **SLV** zijn beursgenoteerde fondsen die de goud- en zilverprijs volgen. Dezelfde indicatoren (RSI, trend, confidence) bepalen hier BUY of HOLD. Onder aan de pagina zie je welke van de twee op dit moment het sterkste signaal heeft.", "en": "**GLD** and **SLV** are exchange-traded funds tracking gold and silver prices. The same indicators (RSI, trend, confidence) determine BUY or HOLD here. At the bottom you see which of the two has the strongest signal right now."},
        "gold_label": {"nl": "Goud (SPDR Gold Shares)", "en": "Gold (SPDR Gold Shares)"},
        "silver_label": {"nl": "Zilver (iShares Silver Trust)", "en": "Silver (iShares Silver Trust)"},
        "buy_signal_buy": {"nl": "🟢 **Koopsignaal: BUY**", "en": "🟢 **Buy signal: BUY**"},
        "buy_signal_hold": {"nl": "🟠 **Koopsignaal: HOLD**", "en": "🟠 **Buy signal: HOLD**"},
        "analysis": {"nl": "**Analyse:**", "en": "**Analysis:**"},
        "threshold": {"nl": "drempel", "en": "threshold"},
        "advice_buy": {"nl": "**Advies:** Koopsignaal voor **{symbol}**. Confidence {conf:.2f} boven drempel.", "en": "**Advice:** Buy signal for **{symbol}**. Confidence {conf:.2f} above threshold."},
        "advice_hold": {"nl": "**Advies:** Geen koop voor **{symbol}**. HOLD aanbevolen.", "en": "**Advice:** No buy for **{symbol}**. HOLD recommended."},
        "best_of_two": {"nl": "**Beste koopsignaal van de twee:** {ticker} ({naam}) — {signal}, confidence {conf:.2f}", "en": "**Best buy signal of the two:** {ticker} ({naam}) — {signal}, confidence {conf:.2f}"},
        "error_load": {"nl": "Kon {symbol} niet laden:", "en": "Could not load {symbol}:"},
        "error_gold": {"nl": "Fout bij Koopsignalen Gold:", "en": "Error on Buy signals Gold:"},
        # Backtest
        "backtest_expander": {"nl": "ℹ️ Wat is een backtest?", "en": "ℹ️ What is a backtest?"},
        "backtest_expander_text": {"nl": "Een **backtest** simuleert wat er was gebeurd als je in het verleden op elk BUY-signaal was ingestapt en bij EXIT weer uitstapte. **Totale return** = groei van je vermogen in die simulatie. **Max drawdown** = grootste daling vanaf een eerdere piek (hoe diep het dal ging). **Equity curve** = verloop van je vermogen in de tijd. **Drawdown** = hoe ver je onder die piek zat. Dit is historisch; de toekomst kan anders zijn.", "en": "A **backtest** simulates what would have happened if you had entered on each BUY signal and exited at EXIT in the past. **Total return** = growth of your capital in that simulation. **Max drawdown** = largest drop from a previous peak (how deep the trough went). **Equity curve** = your capital over time. **Drawdown** = how far below that peak. This is historical; the future may differ."},
        "total_return": {"nl": "Totale return", "en": "Total return"},
        "total_return_help": {"nl": "Opbrengst van de strategie over de hele periode (gesimuleerd).", "en": "Strategy return over the full period (simulated)."},
        "max_dd_help": {"nl": "Grootste daling t.o.v. een eerdere piek; hoe diep het ergste dal was.", "en": "Largest decline from a previous peak; how deep the worst trough was."},
        "trades_help": {"nl": "Aantal in- en uitstappen in de backtest.", "en": "Number of entries and exits in the backtest."},
        "equity_caption": {"nl": "Equity curve — verloop van vermogen in de tijd (1 = start)", "en": "Equity curve — capital over time (1 = start)"},
        "drawdown_caption": {"nl": "Drawdown — hoe ver onder de eerdere piek (0 = op piek, -20% = 20% onder piek)", "en": "Drawdown — how far below the previous peak (0 = at peak, -20% = 20% below peak)"},
        "trades_title": {"nl": "Trades (met entry labels)", "en": "Trades (with entry labels)"},
        "no_trades_backtest": {"nl": "Geen trades met deze instellingen.", "en": "No trades with these settings."},
        "d_conditional_title": {"nl": "D — Conditional stats per setup/bucket", "en": "D — Conditional stats per setup/bucket"},
        "no_stats": {"nl": "Nog geen stats (geen trades).", "en": "No stats yet (no trades)."},
        "expectancy_expander": {"nl": "ℹ️ Uitleg expectancy & profit factor", "en": "ℹ️ Expectancy & profit factor explained"},
        "expectancy_expander_text": {"nl": "- **Expectancy** (per trade): verwachte opbrengst per trade; boven 0 betekent de strategie gemiddeld winst.\n- **Profit factor**: totaal winst / totaal verlies; boven 1 = er werd meer verdiend dan verloren.\n- **Winrate**: % winnende trades. Let op: veel trades (sample size) geeft betrouwbaardere cijfers.", "en": "- **Expectancy** (per trade): expected return per trade; above 0 means the strategy is profitable on average.\n- **Profit factor**: total profit / total loss; above 1 = more was won than lost.\n- **Win rate**: % of winning trades. Note: more trades (sample size) gives more reliable figures."},
        "interpretation": {"nl": "Interpretatie: Expectancy/trade > 0 = edge; Profit factor > 1 = winst som > verlies som; let op sample size (trades).", "en": "Interpretation: Expectancy/trade > 0 = edge; Profit factor > 1 = profit sum > loss sum; mind sample size (trades)."},
        "error_backtest": {"nl": "Fout bij Backtest:", "en": "Error on Backtest:"},
        # Export
        "export_info": {"nl": "Volgende stap: export signals.csv / trades.csv / stats.csv / equity.csv.", "en": "Next step: export signals.csv / trades.csv / stats.csv / equity.csv."},
    }

T = _tr()
if "lang" not in st.session_state:
    st.session_state.lang = "nl"

def t(key: str, **kwargs) -> str:
    s = T.get(key, {}).get(st.session_state.lang, T.get(key, {}).get("nl", key))
    return s.format(**kwargs) if kwargs else s

# =========================
# App setup
# =========================
APP_VERSION = "v1.11 - Koersdata + Signals + Watchlist + Risk"
st.set_page_config(page_title="Darbyshire Trading Tool", layout="wide")
st.title("Darbyshire Trading Tool")
st.caption(APP_VERSION)
st.caption(t("disclaimer"))

load_dotenv()
API_KEY = os.environ.get("TWELVE_DATA_API_KEY")
BASE_URL = "https://api.twelvedata.com/time_series"

# =========================
# Sidebar
# =========================
WATCHLIST_TICKERS = ["SOXL", "TQQQ", "NVDA", "SPY", "QQQ"]
PAGE_KEYS = ["Home", "Koersdata", "Signals", "Watchlist", "Optimizer", "Koopsignalen Gold", "S&P 500", "Backtest", "Export (later)"]
with st.sidebar:
    lang_choice = st.radio("Language / Taal", ["🇳🇱 Nederlands", "🇬🇧 English"], horizontal=True)
    st.session_state.lang = "nl" if "Nederlands" in lang_choice else "en"
    st.header(t("menu"))
    _page_labels = ["page_home", "page_koersdata", "page_signals", "page_watchlist", "page_optimizer", "page_gold", "page_sp500", "page_backtest", "page_export"]
    page_index = st.radio(t("choose"), range(len(PAGE_KEYS)), format_func=lambda i: t(_page_labels[i]))
    page = PAGE_KEYS[page_index]

    # ----- Configurator & Koopsignaal (bovenaan, direct zichtbaar) -----
    st.divider()
    st.subheader("⚙️ " + t("configurator_title"))
    day_move_pct = st.slider(t("day_move_label"), -10.0, 10.0, 0.0, 0.5, help=t("day_move_help"))

    # Marktfilter: gebruik S&P 500 om BUY te filteren
    market_filter_enabled = st.checkbox(
        t("market_filter_label"),
        value=False,
        help=t("market_filter_help"),
    )

    # Profiel-presets voor basisinstellingen (zet defaults in session_state)
    st.divider()
    st.subheader("🧬 Profiel")
    profile_options = ["standard", "conservative", "aggressive"]
    def _profile_label(p: str) -> str:
        if p == "conservative":
            return "Conservatief"
        if p == "aggressive":
            return "Aggressief"
        return "Standaard"
    profile = st.radio("Profiel", profile_options, format_func=_profile_label)

    profile_defaults = {
        "standard":     {"buy_th": 0.65, "min_prob_4": 25, "risk_pct": 1.0, "stop_pct": 8.0},
        "conservative": {"buy_th": 0.72, "min_prob_4": 30, "risk_pct": 0.5, "stop_pct": 6.0},
        "aggressive":   {"buy_th": 0.58, "min_prob_4": 20, "risk_pct": 1.5, "stop_pct": 10.0},
    }
    if "current_profile" not in st.session_state:
        st.session_state.current_profile = profile
    if profile != st.session_state.current_profile:
        pvals = profile_defaults[profile]
        st.session_state["buy_threshold_slider"] = pvals["buy_th"]
        st.session_state["min_prob_4pct_slider"] = pvals["min_prob_4"]
        st.session_state["max_risk_pct_slider"] = pvals["risk_pct"]
        st.session_state["stop_pct_slider"] = pvals["stop_pct"]
        st.session_state.current_profile = profile

    # Koopsignaal-criterium (werkt samen met profiel)
    st.subheader("📊 " + t("buy_criterion_label"))
    buy_criterion = st.radio(
        "Optie",
        ["confidence", "prob_4pct_20"],
        format_func=lambda x: t("buy_criterion_confidence") if x == "confidence" else t("buy_criterion_4pct"),
        help=t("signal_basis_explanation"),
    )
    min_prob_raw = st.slider(
        t("min_prob_4pct_label"), 10, 50, 25, 5,
        key="min_prob_4pct_slider",
        help=t("min_prob_4pct_help"),
        disabled=(buy_criterion != "prob_4pct_20"),
    )
    min_prob_4pct = min_prob_raw / 100.0

    st.divider()
    # Watchlist: snelle keuze voor favoriete tickers
    st.subheader("⭐ " + t("watchlist_title"))
    st.caption(t("watchlist_help"))
    fav_cols = st.columns(len(WATCHLIST_TICKERS))
    for col, sym in zip(fav_cols, WATCHLIST_TICKERS):
        if col.button(sym):
            st.session_state["sidebar_ticker_input"] = sym

    # Vrije invoer US ticker (gesynchroniseerd met watchlist)
    raw_ticker = st.text_input(
        t("us_ticker"),
        value=st.session_state.get("sidebar_ticker_input", "SOXL"),
        key="sidebar_ticker_input",
        help=t("us_ticker_help"),
    )
    ticker = raw_ticker.strip().upper()
    days = st.slider(t("days_data"), 300, 2500, 1200, help=t("days_data_help"))

    st.subheader(t("signal_settings"))
    rsi_period = st.slider(t("rsi_period"), 5, 30, 14, help=t("rsi_period_help"))
    buy_threshold = st.slider("BUY threshold", 0.50, 0.95, 0.65, 0.01, key="buy_threshold_slider", help=t("buy_threshold_help"))

    st.divider()
    st.subheader(t("backtest_settings"))
    exit_threshold = st.slider("EXIT threshold", 0.10, 0.60, 0.30, 0.01, help=t("exit_threshold_help"))
    max_hold_days = st.slider("Max hold days", 2, 180, 20, help=t("max_hold_help"))

    # Risk / position sizing
    st.divider()
    st.subheader("🧮 " + t("risk_sidebar_title"))
    # Use session_state so we can overwrite from IB
    if "account_size_usd" not in st.session_state:
        st.session_state.account_size_usd = 10000.0
    account_size = st.number_input(
        t("account_size_label"),
        min_value=0.0,
        step=500.0,
        help=t("account_size_help"),
        key="account_size_usd",
    )
    max_trade_risk_pct_raw = st.slider(
        t("max_risk_pct_label"),
        0.25, 5.0, 1.0, 0.25,
        key="max_risk_pct_slider",
        help=t("max_risk_pct_help"),
    )
    max_trade_risk_pct = max_trade_risk_pct_raw / 100.0
    stop_pct = st.slider(
        t("stop_pct_label"),
        1.0, 25.0, 8.0, 0.5,
        key="stop_pct_slider",
        help=t("stop_pct_help"),
    )
    st.divider()
    st.subheader(t("conf_buckets"))
    st.caption(t("buckets_caption"))
    b1 = st.slider("Bucket 1 end", 0.50, 0.80, 0.60, 0.01, help=t("bucket1_help"))
    b2 = st.slider("Bucket 2 end", 0.55, 0.90, 0.70, 0.01, help=t("bucket2_help"))
    b3 = st.slider("Bucket 3 end", 0.60, 0.95, 0.80, 0.01, help=t("bucket3_help"))

    st.divider()
    st.subheader(t("recommended_title"))
    compare_tickers = st.text_input(
        t("compare_label"),
        value="",
        placeholder=t("compare_placeholder"),
        help=t("compare_help"),
        key="sidebar_compare_tickers",
    ).strip()

    st.divider()
    st.write(t("debug"))
    st.write(t("api_key_present"), "✅" if API_KEY else "❌")

# Marktfilter op basis van SPY (S&P 500)
market_ok = True
market_filter_message = ""
if market_filter_enabled:
    try:
        df_spy = build_signal_df("SPY")
        latest_spy = df_spy.iloc[-1]
        spy_signal = str(latest_spy["signal"])
        spy_ema50 = float(latest_spy["ema50"])
        spy_ema200 = float(latest_spy["ema200"])
        spy_trend_up = spy_ema50 > spy_ema200
        market_ok = (spy_signal == "BUY") and spy_trend_up
        market_filter_message = t("market_filter_ok") if market_ok else t("market_filter_blocked")
    except Exception:
        # Als SPY niet geladen kan worden, negeren we het filter om geen trades te blokkeren
        market_ok = True
        market_filter_message = ""

# =========================
# Data ophalen
# =========================
@st.cache_data(show_spinner=False)
def fetch_data(symbol: str, outputsize: int = 4000) -> pd.DataFrame:
    if not API_KEY:
        raise RuntimeError("Geen TWELVE_DATA_API_KEY gevonden in .env")

    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": outputsize,
        "apikey": API_KEY,
        "format": "JSON",
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    if "values" not in data:
        raise RuntimeError(f"Geen 'values' in response voor {symbol}: {data}")

    df = pd.DataFrame(data["values"]).rename(columns={"datetime": "date"})
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df = df.dropna(subset=["open", "high", "low", "close"])
    return df

# =========================
# Indicatoren
# =========================
def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return (100 - (100 / (1 + rs))).bfill()

def add_indicators(df: pd.DataFrame, rsi_p: int) -> pd.DataFrame:
    df = df.copy()

    # Trend
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

    # RSI
    df["rsi"] = rsi(df["close"], rsi_p)

    # Momentum
    df["roc10"] = df["close"].pct_change(10)

    # Volatility proxy
    df["range_pct"] = (df["high"] - df["low"]) / df["close"]

    # Market regime
    df["trend_up"] = (df["ema50"] > df["ema200"]).astype(int)

    return df

def compute_confidence(df: pd.DataFrame) -> pd.Series:
    # 1) Mean reversion (RSI)
    rsi_score = ((55 - df["rsi"].clip(0, 100)) / 30).clip(0, 1)

    # 2) Trend
    trend_score = (
        (df["ema20"] > df["ema50"]).astype(int) * 0.6 +
        (df["ema50"] > df["ema200"]).astype(int) * 0.4
    )

    # 3) Momentum
    momentum_score = (df["roc10"].fillna(0) / 0.05).clip(0, 1)

    # 4) Volatility sanity
    vol_score = (df["range_pct"].clip(0, 0.1) / 0.04).clip(0, 1)

    return (
        0.35 * rsi_score +
        0.30 * trend_score +
        0.20 * momentum_score +
        0.15 * vol_score
    ).clip(0, 1)

# =========================
# Rule-based setups (A)
# =========================
def rsi_zone(val: float) -> str:
    if val <= 30:
        return "oversold"
    if val >= 70:
        return "overbought"
    return "neutral"

def compute_setup_label(row: pd.Series) -> str:
    """
    Rule-based labels (A):
    - Bird: oversold-ish mean reversion + improving short trend
    - Green: trend continuation (bull regime + pullback-ish)
    - Grey: range/indecision
    """
    r = float(row["rsi"])
    ema20 = float(row["ema20"])
    ema50 = float(row["ema50"])
    ema200 = float(row["ema200"])
    roc10 = float(row["roc10"]) if pd.notna(row["roc10"]) else 0.0

    short_up = ema20 > ema50
    bull = ema50 > ema200

    # Bird = dip/mean-reversion setup
    if (r <= 38) and short_up and (roc10 > -0.10):
        return "Bird"

    # Green = trend continuation
    if bull and short_up and (r >= 40) and (roc10 >= 0):
        return "Green"

    # Grey = no-man's land / choppy
    if (not bull) and (38 < r < 55):
        return "Grey"

    return "None"

def make_conf_buckets(series: pd.Series, b1: float, b2: float, b3: float) -> pd.Series:
    edges = sorted([b1, b2, b3])
    b1, b2, b3 = edges[0], edges[1], edges[2]
    bins = [0.0, b1, b2, b3, 1.00001]
    labels = [f"0.00-{b1:.2f}", f"{b1:.2f}-{b2:.2f}", f"{b2:.2f}-{b3:.2f}", f"{b3:.2f}-1.00"]
    return pd.cut(series.clip(0, 1), bins=bins, labels=labels, include_lowest=True)

# =========================
# Prognose bij veronderstelde dagbeweging
# =========================
def prognosis_for_daily_move(
    df: pd.DataFrame,
    move_pct: float,
    rsi_p: int,
    buy_th: float,
    b1: float, b2: float, b3: float,
) -> dict | None:
    """Gegeven huidige data: als de slotkoers vandaag move_pct% beweegt, welk signaal zou dat geven?"""
    if move_pct == 0:
        return None
    ohlc = df[["date", "open", "high", "low", "close"]].copy()
    last = ohlc.iloc[-1]
    next_close = float(last["close"]) * (1 + move_pct / 100)
    next_open = float(last["close"])
    next_high = max(next_open, next_close)
    next_low = min(next_open, next_close)
    next_date = last["date"] + pd.Timedelta(days=1) if pd.api.types.is_datetime64_any_dtype(ohlc["date"]) else last["date"]
    new_row = pd.DataFrame([{
        "date": next_date,
        "open": next_open,
        "high": next_high,
        "low": next_low,
        "close": next_close,
    }])
    extended = pd.concat([ohlc, new_row], ignore_index=True)
    extended = add_indicators(extended, rsi_p)
    conf_series = compute_confidence(extended)
    conf = float(conf_series.iloc[-1])
    sig = "BUY" if conf >= buy_th else "HOLD"
    rsi_val = float(extended["rsi"].iloc[-1])
    setup = compute_setup_label(extended.iloc[-1])
    bucket = make_conf_buckets(conf_series.iloc[[-1]], b1, b2, b3).iloc[0]
    return {"signal": sig, "confidence": conf, "rsi": rsi_val, "setup": setup, "conf_bucket": str(bucket)}

# =========================
# Build signal df
# =========================
def build_signal_df(symbol: str | None = None) -> pd.DataFrame:
    sym = symbol if symbol else ticker
    raw = fetch_data(sym, outputsize=days + 600)
    df = raw.tail(days).reset_index(drop=True)
    df = add_indicators(df, rsi_period)

    df["confidence"] = compute_confidence(df)
    df["signal"] = (df["confidence"] >= buy_threshold).map({True: "BUY", False: "HOLD"})

    df["rsi_zone"] = df["rsi"].apply(lambda x: rsi_zone(float(x)))
    df["setup"] = df.apply(compute_setup_label, axis=1)
    df["conf_bucket"] = make_conf_buckets(df["confidence"], b1, b2, b3)

    return df

# =========================
# Backtest engine (Equity + Trades annotated)
# =========================
def run_backtest_equity(df: pd.DataFrame):
    df = df.copy().reset_index(drop=True)

    trades = []
    equity = 1.0
    in_trade = False
    entry_price = entry_date = entry_idx = None
    entry_conf = entry_setup = entry_bucket = entry_rsi_zone = None

    equity_series = []

    for i in range(len(df)):
        row = df.iloc[i]

        # Entry
        if (not in_trade) and row["signal"] == "BUY" and i < len(df) - 1:
            entry_idx = i + 1
            entry_price = float(df.iloc[entry_idx]["open"])
            entry_date = df.iloc[entry_idx]["date"]

            # Store context of SIGNAL day
            entry_conf = float(row["confidence"])
            entry_setup = str(row["setup"])
            entry_bucket = str(row["conf_bucket"])
            entry_rsi_zone = str(row["rsi_zone"])

            in_trade = True
            equity_series.append({"date": row["date"], "equity": equity})
            continue

        # Flat
        if not in_trade:
            equity_series.append({"date": row["date"], "equity": equity})
            continue

        # Mark-to-market
        if i == entry_idx:
            equity *= float(row["close"]) / entry_price
        else:
            equity *= float(row["close"]) / float(df.iloc[i - 1]["close"])

        equity_series.append({"date": row["date"], "equity": equity})

        # Exit
        days_in_trade = i - entry_idx
        if float(row["confidence"]) < exit_threshold or days_in_trade >= max_hold_days:
            exit_price = float(row["close"])
            exit_date = row["date"]
            ret = (exit_price - entry_price) / entry_price

            trades.append({
                "entry_date": entry_date,
                "entry_price": entry_price,
                "exit_date": exit_date,
                "exit_price": exit_price,
                "days": days_in_trade,
                "return_pct": ret,
                "entry_confidence": entry_conf,
                "entry_setup": entry_setup,
                "entry_bucket": entry_bucket,
                "entry_rsi_zone": entry_rsi_zone,
            })

            in_trade = False
            entry_price = entry_date = entry_idx = None
            entry_conf = entry_setup = entry_bucket = entry_rsi_zone = None

    eq = pd.DataFrame(equity_series).drop_duplicates(subset=["date"]).reset_index(drop=True)
    eq["date"] = pd.to_datetime(eq["date"])
    eq = eq.sort_values("date").reset_index(drop=True)
    eq["peak"] = eq["equity"].cummax()
    eq["drawdown"] = eq["equity"] / eq["peak"] - 1.0

    trades_df = pd.DataFrame(trades)
    return trades_df, eq


def run_backtest_equity_params(df: pd.DataFrame, exit_th: float, max_hold: int):
    """Variant van run_backtest_equity met lokale exit/hold-parameters (voor optimizer)."""
    df = df.copy().reset_index(drop=True)

    trades = []
    equity = 1.0
    in_trade = False
    entry_price = entry_date = entry_idx = None
    entry_conf = entry_setup = entry_bucket = entry_rsi_zone = None

    equity_series = []

    for i in range(len(df)):
        row = df.iloc[i]

        # Entry
        if (not in_trade) and row["signal"] == "BUY" and i < len(df) - 1:
            entry_idx = i + 1
            entry_price = float(df.iloc[entry_idx]["open"])
            entry_date = df.iloc[entry_idx]["date"]

            entry_conf = float(row["confidence"])
            entry_setup = str(row["setup"])
            entry_bucket = str(row["conf_bucket"])
            entry_rsi_zone = str(row["rsi_zone"])

            in_trade = True
            equity_series.append({"date": row["date"], "equity": equity})
            continue

        # Flat
        if not in_trade:
            equity_series.append({"date": row["date"], "equity": equity})
            continue

        # Mark-to-market
        if i == entry_idx:
            equity *= float(row["close"]) / entry_price
        else:
            equity *= float(row["close"]) / float(df.iloc[i - 1]["close"])

        equity_series.append({"date": row["date"], "equity": equity})

        # Exit
        days_in_trade = i - entry_idx
        if float(row["confidence"]) < exit_th or days_in_trade >= max_hold:
            exit_price = float(row["close"])
            exit_date = row["date"]
            ret = (exit_price - entry_price) / entry_price

            trades.append({
                "entry_date": entry_date,
                "entry_price": entry_price,
                "exit_date": exit_date,
                "exit_price": exit_price,
                "days": days_in_trade,
                "return_pct": ret,
                "entry_confidence": entry_conf,
                "entry_setup": entry_setup,
                "entry_bucket": entry_bucket,
                "entry_rsi_zone": entry_rsi_zone,
            })

            in_trade = False
            entry_price = entry_date = entry_idx = None
            entry_conf = entry_setup = entry_bucket = entry_rsi_zone = None

    eq = pd.DataFrame(equity_series).drop_duplicates(subset=["date"]).reset_index(drop=True)
    eq["date"] = pd.to_datetime(eq["date"])
    eq = eq.sort_values("date").reset_index(drop=True)
    eq["peak"] = eq["equity"].cummax()
    eq["drawdown"] = eq["equity"] / eq["peak"] - 1.0

    trades_df = pd.DataFrame(trades)
    return trades_df, eq

# =========================
# Conditional stats (D)
# =========================
def group_trade_stats(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()

    out = []
    for (setup, bucket), g in trades.groupby(["entry_setup", "entry_bucket"], dropna=False):
        wins = g[g["return_pct"] > 0]["return_pct"]
        losses = g[g["return_pct"] <= 0]["return_pct"]

        winrate = (g["return_pct"] > 0).mean()
        avg_win = wins.mean() if not wins.empty else 0.0
        avg_loss = abs(losses.mean()) if not losses.empty else 0.0
        expectancy = (winrate * avg_win) - ((1 - winrate) * avg_loss)

        profit_factor = (wins.sum() / abs(losses.sum())) if not losses.empty else float("inf")

        # Kans op 4%+ winst: alle trades, en alleen trades die binnen 20 dagen werden gesloten
        prob_4pct = (g["return_pct"] >= 0.04).mean()
        g_20d = g[g["days"] <= 20]
        prob_4pct_20d = (g_20d["return_pct"] >= 0.04).mean() if len(g_20d) >= 3 else float("nan")
        n_20d = len(g_20d)

        out.append({
            "setup": setup,
            "bucket": bucket,
            "trades": len(g),
            "winrate": winrate,
            "avg_return": g["return_pct"].mean(),
            "median_return": g["return_pct"].median(),
            "avg_days": g["days"].mean(),
            "expectancy": expectancy,
            "profit_factor": profit_factor,
            "prob_4pct": prob_4pct,
            "prob_4pct_20d": prob_4pct_20d,
            "n_trades_20d": n_20d,
        })

    stats = pd.DataFrame(out)
    stats = stats.sort_values(["setup", "bucket"]).reset_index(drop=True)
    return stats

@st.cache_data(show_spinner=False)
def run_full_analysis(symbol: str, days: int, rsi_p: int, buy_th: float, exit_th: float, max_hold: int, b1: float, b2: float, b3: float):
    df = build_signal_df()
    trades, eq = run_backtest_equity(df)
    stats = group_trade_stats(trades)
    return df, trades, eq, stats

# =========================
# Pages
# =========================
if page == "Home":
    st.subheader(t("home_title"))
    st.write(t("home_bullet1") + "\n" + t("home_bullet2") + "\n" + t("home_bullet3"))
    with st.expander(t("home_expander")):
        st.markdown(t("home_expander_text"))

elif page == "Koersdata":
    st.subheader(f"{t('page_koersdata')} — {ticker}")
    with st.expander(t("koersdata_cols_title")):
        st.markdown(t("koersdata_cols_text"))
    try:
        df = build_signal_df()
        show_cols = [
            "date", "open", "high", "low", "close", "volume",
            "rsi", "ema20", "ema50", "ema200",
            "roc10", "range_pct",
            "confidence", "conf_bucket", "setup", "signal"
        ]
        st.dataframe(df[show_cols].tail(300), width="stretch")

        st.caption(t("chart_close"))
        st.line_chart(df.set_index("date")[["close"]], width="stretch")

    except Exception as e:
        st.error(f"{t('error_koersdata')} {e}")

elif page == "Signals":
    st.subheader(f"{t('page_signals')} — {ticker}")
    with st.expander(t("signals_expander")):
        st.markdown(t("signals_expander_text"))
    try:
        df, trades, eq, stats = run_full_analysis(
            ticker, days, rsi_period,
            buy_threshold, exit_threshold, max_hold_days,
            b1, b2, b3
        )
        latest = df.iloc[-1]

        # ---------- ANALYSE & KOOPSIGNAAL (SUMMARY) ----------
        st.divider()
        signal_now = str(latest["signal"])  # op basis van confidence
        conf_now = float(latest["confidence"])
        rsi_now = float(latest["rsi"])
        setup_now = str(latest["setup"])
        bucket_now = str(latest["conf_bucket"])
        ema20 = float(latest["ema20"])
        ema50 = float(latest["ema50"])
        ema200 = float(latest["ema200"])
        trend_short = "bullish" if ema20 > ema50 else "bearish"
        trend_long = "bullish" if ema50 > ema200 else "bearish"

        # Effectief signaal: confidence OF kans op 4% in 20 dagen
        prob_4pct_20d_now = float("nan")
        if buy_criterion == "prob_4pct_20" and not stats.empty:
            match = stats[(stats["setup"] == setup_now) & (stats["bucket"] == bucket_now)]
            if not match.empty and "prob_4pct_20d" in match.columns:
                prob_4pct_20d_now = float(match["prob_4pct_20d"].iloc[0])
        if buy_criterion == "prob_4pct_20":
            effective_signal = "BUY" if (pd.notna(prob_4pct_20d_now) and prob_4pct_20d_now >= min_prob_4pct) else "HOLD"
        else:
            effective_signal = signal_now

        # Marktfilter toepassen (SPY moet zelf BUY + opwaartse trend hebben)
        if market_filter_enabled and not market_ok:
            effective_signal = "HOLD"

        if effective_signal == "BUY":
            st.success(t("summary_buy_box"))
        else:
            st.warning(t("summary_hold_box"))

        with st.expander(t("summary_expander"), expanded=True):
            if buy_criterion == "confidence":
                st.caption(t("signal_basis_explanation"))
            else:
                st.caption(t("signal_4pct_explanation", pct=min_prob_4pct * 100))
                if pd.notna(prob_4pct_20d_now):
                    st.caption(f"{t('kans_4pct_label')}: **{prob_4pct_20d_now:.0%}**")
                else:
                    st.caption(t("geen_data_4pct"))
            if market_filter_enabled and market_filter_message:
                st.caption(market_filter_message)
            st.markdown(t("summary_brief_analysis"))
            st.markdown(f"- **RSI({rsi_period}):** {rsi_now:.1f} ({rsi_zone(rsi_now)})")
            st.markdown(f"- **Trend:** {trend_short} / {trend_long}")
            st.markdown(f"- **Setup:** {setup_now} · **Bucket:** {bucket_now}")
            st.markdown(f"- **Confidence:** {conf_now:.2f} ({t('threshold')} BUY = {buy_threshold})")
            if effective_signal == "BUY":
                st.markdown(t("advice_buy", symbol=ticker, conf=conf_now))
            else:
                st.markdown(t("advice_hold", symbol=ticker))

        # ---------- RISK / POSITIE–GROOTTE VOOR HUIDIGE TICKER ----------
        if account_size > 0 and max_trade_risk_pct > 0 and stop_pct > 0:
            max_risk_amount = account_size * max_trade_risk_pct
            price_now = float(latest["close"])
            stop_price = price_now * (1 - stop_pct / 100.0)
            per_share_loss = max(price_now - stop_price, 0.0)
            st.divider()
            st.subheader(t("risk_block_title"))
            if per_share_loss <= 0 or max_risk_amount <= 0:
                st.info(t("risk_too_small"))
            else:
                max_shares = int(max_risk_amount // per_share_loss)
                if max_shares <= 0:
                    st.info(t("risk_too_small"))
                else:
                    exposure = max_shares * price_now
                    st.info(
                        t(
                            "risk_summary",
                            account=account_size,
                            risk_pct=max_trade_risk_pct * 100,
                            stop_pct=stop_pct,
                            price=price_now,
                            shares=max_shares,
                            ticker=ticker,
                            exposure=exposure,
                            risk_amount=max_risk_amount,
                        )
                    )

        # ---------- KANS-KAARTJE VOOR HUIDIG SIGNAAL ----------
        st.divider()
        st.subheader(t("trade_card_title"))
        trade_card = None
        if not trades.empty:
            current_trades = trades[
                (trades["entry_setup"] == setup_now) &
                (trades["entry_bucket"] == bucket_now)
            ].copy()
            if not current_trades.empty:
                wins_c = current_trades[current_trades["return_pct"] > 0]["return_pct"]
                winrate_c = float((current_trades["return_pct"] > 0).mean())
                median_c = float(current_trades["return_pct"].median())
                trades_20d_c = current_trades[current_trades["days"] <= 20]
                prob_4pct_20d_c = float("nan")
                if len(trades_20d_c) >= 3:
                    prob_4pct_20d_c = float((trades_20d_c["return_pct"] >= 0.04).mean())
                trade_card = {
                    "winrate": winrate_c,
                    "median": median_c,
                    "prob_4pct_20d": prob_4pct_20d_c,
                }

        if trade_card is None:
            st.info(t("trade_card_no_data"))
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric(t("winrate"), f"{trade_card['winrate']:.1%}", help=t("winrate_help"))
            if pd.notna(trade_card["prob_4pct_20d"]):
                c2.metric(t("prob_4pct_20d_label"), f"{trade_card['prob_4pct_20d']:.0%}", help=t("prob_4pct_20d_help"))
            else:
                c2.metric(t("prob_4pct_20d_label"), "n/a", help=t("prob_4pct_20d_help"))
            c3.metric(t("median_trade"), f"{trade_card['median']:.2%}", help=t("median_trade_help"))

        # ---------- AANBEVOLEN TICKER (beste kans van slagen) ----------
        ticker_list = [s.strip().upper() for s in compare_tickers.split(",") if s.strip()][:5]
        if ticker_list:
            st.subheader(t("recommended_title"))
            rows = []
            failed = []
            with st.spinner(t("loading_compare")):
                for i, sym in enumerate(ticker_list):
                    if i > 0:
                        time.sleep(0.8)
                    try:
                        sdf = build_signal_df(sym)
                        r = sdf.iloc[-1]
                        rows.append({
                            "ticker": sym,
                            "signal": str(r["signal"]),
                            "confidence": float(r["confidence"]),
                            "rsi": float(r["rsi"]),
                            "setup": str(r["setup"]),
                        })
                    except Exception as e:
                        failed.append(f"{sym} ({str(e)[:50]})")
            if rows:
                comp_df = pd.DataFrame(rows)
                comp_df["_order"] = (comp_df["signal"] != "BUY").astype(int) * 1000 - comp_df["confidence"]
                comp_df = comp_df.sort_values("_order").drop(columns=["_order"])
                best = comp_df.iloc[0]
                if best["signal"] == "BUY":
                    st.success("🟢 " + t("buy_recommendation", ticker=best["ticker"]))
                else:
                    st.warning("🟠 " + t("buy_recommendation_none"))
                st.info(t("recommended_info", ticker=best["ticker"], signal=best["signal"], conf=best["confidence"], rsi=best["rsi"], setup=best["setup"]))
                st.dataframe(comp_df, width="stretch", hide_index=True)
                if failed:
                    st.caption("⚠️ " + t("compare_failed") + ", ".join(failed))
            else:
                st.warning(t("no_tickers_loaded"))
                if failed:
                    st.caption("Failed: " + ", ".join(failed))
        else:
            st.caption("💡 " + t("compare_hint"))

        # ---------- PROGNOSE BIJ VERONDERSTELDE DAGBEWEGING ----------
        if day_move_pct != 0:
            st.subheader(t("prognosis_title"))
            prog = prognosis_for_daily_move(df, day_move_pct, rsi_period, buy_threshold, b1, b2, b3)
            if prog:
                pct_abs = abs(day_move_pct)
                if day_move_pct < 0:
                    msg = t("prognosis_down", pct=pct_abs, signal=prog["signal"], conf=prog["confidence"], rsi=prog["rsi"], setup=prog["setup"])
                else:
                    msg = t("prognosis_up", pct=day_move_pct, signal=prog["signal"], conf=prog["confidence"], rsi=prog["rsi"], setup=prog["setup"])
                if prog["signal"] == "BUY":
                    st.success(msg)
                else:
                    st.info(msg)
        st.divider()

        # --- LIVE SIGNAL (NU)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Signal", latest["signal"], help=t("signal_help"))
        c2.metric("Confidence", f"{latest['confidence']:.2f}", help=t("confidence_help"))
        c3.metric(f"RSI({rsi_period})", f"{latest['rsi']:.1f}", help=t("rsi_help"))
        c4.metric("Setup", str(latest["setup"]), help=t("setup_help"))
        c5.metric("Bucket", str(latest["conf_bucket"]), help=t("bucket_help"))
        st.caption(t("live_caption"))
        cols = [
            "date","open","high","low","close",
            "rsi","ema20","ema50","ema200",
            "roc10","range_pct",
            "confidence","conf_bucket",
            "rsi_zone","setup","signal"
        ]
        st.dataframe(df[cols].sort_values("date", ascending=False).head(200), width="stretch")

        # --- HISTORISCHE VERWACHTING BIJ DIT SIGNAAL
        st.divider()
        st.subheader(t("hist_exp_title"))

        if trades.empty:
            st.warning(t("no_trades_warn"))
        else:
            setup_now = str(latest["setup"])
            bucket_now = str(latest["conf_bucket"])

            subset = trades[
                (trades["entry_setup"] == setup_now) &
                (trades["entry_bucket"] == bucket_now)
            ].copy()

            if subset.empty:
                st.info(t("no_hist_trades"))
            else:
                subset["month"] = subset["entry_date"].dt.to_period("M")
                monthly = subset.groupby("month")["return_pct"].sum().dropna()

                if len(monthly) >= 6:
                    p50 = float(monthly.quantile(0.50))
                    p05 = float(monthly.quantile(0.05))
                    prob_pos = float((monthly > 0).mean())
                    

                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric(t("median_month"), f"{p50:.1%}", help=t("median_month_help"))
                    k2.metric(t("prob_pos_month"), f"{prob_pos:.0%}", help=t("prob_pos_help"))
                    k3.metric(t("p05_label"), f"{p05:.1%}", help=t("p05_help"))
                    k4.metric(t("n_trades"), int(len(subset)), help=t("n_trades_help"))

                    st.caption(t("conditional_caption"))
                else:
                    st.info(t("few_samples"))

                # Trade-level stats (altijd)
                wins = subset[subset["return_pct"] > 0]["return_pct"]
                losses = subset[subset["return_pct"] <= 0]["return_pct"]

                winrate = float((subset["return_pct"] > 0).mean())
                avg_win = float(wins.mean()) if not wins.empty else 0.0
                avg_loss = float(abs(losses.mean())) if not losses.empty else 0.0
                expectancy = (winrate * avg_win) - ((1 - winrate) * avg_loss)

                # Kans op ≥4% binnen 20 dagen, alleen tonen bij voldoende samples
                subset_20d = subset[subset["days"] <= 20]
                prob_4pct_20d_local = float("nan")
                if len(subset_20d) >= 3:
                    prob_4pct_20d_local = float((subset_20d["return_pct"] >= 0.04).mean())

                t1, t2, t3, t4 = st.columns(4)
                t1.metric(t("winrate"), f"{winrate:.1%}", help=t("winrate_help"))
                t2.metric(t("expectancy"), f"{expectancy:.2%}", help=t("expectancy_help"))
                if pd.notna(prob_4pct_20d_local):
                    t3.metric(t("prob_4pct_20d_label"), f"{prob_4pct_20d_local:.0%}", help=t("prob_4pct_20d_help"))
                else:
                    t3.metric(t("prob_4pct_20d_label"), "n/a", help=t("prob_4pct_20d_help"))
                t4.metric(t("avg_hold"), f"{float(subset['days'].mean()):.1f}", help=t("avg_hold_help"))

        # Overzicht D
        st.divider()
        st.subheader(t("overview_d"))
        with st.expander(t("conditional_stats_exp")):
            st.markdown(t("conditional_stats_text"))
        if stats.empty:
            st.info(t("no_conditional"))
        else:
            st.dataframe(stats, width="stretch")

    except Exception as e:
        st.error(f"{t('error_signals')} {e}")

elif page == "Watchlist":
    st.subheader(t("watchlist_page_title"))
    st.caption(t("watchlist_page_intro"))

    rows = []
    failed_syms = []
    for sym in WATCHLIST_TICKERS:
        try:
            df_w, trades_w, eq_w, stats_w = run_full_analysis(
                sym, days, rsi_period, buy_threshold, exit_threshold, max_hold_days, b1, b2, b3
            )
            latest_w = df_w.iloc[-1]
            trades_20d = trades_w[trades_w["days"] <= 20]
            prob_4pct_20d = float("nan")
            if not trades_20d.empty:
                prob_4pct_20d = float((trades_20d["return_pct"] >= 0.04).mean())
            rows.append({
                "ticker": sym,
                "signal": str(latest_w["signal"]),
                "confidence": float(latest_w["confidence"]),
                "rsi": float(latest_w["rsi"]),
                "setup": str(latest_w["setup"]),
                "bucket": str(latest_w["conf_bucket"]),
                "prob_4pct_20d": prob_4pct_20d,
                "trades_20d": 0 if trades_20d.empty else int(len(trades_20d)),
            })
        except Exception:
            failed_syms.append(sym)

    if rows:
        df_watch = pd.DataFrame(rows)
        # Ranking: eerst BUY, dan hoogste probability 4% in 20d, dan hoogste confidence
        df_watch["_order"] = (
            (df_watch["signal"] != "BUY").astype(int) * 1000
            - df_watch["prob_4pct_20d"].fillna(0) * 100
            - df_watch["confidence"] * 10
        )
        df_watch = df_watch.sort_values("_order").drop(columns=["_order"])
        best = df_watch.iloc[0]
        if best["signal"] == "BUY":
            st.success("🟢 " + t("buy_recommendation", ticker=best["ticker"]))
        else:
            st.warning("🟠 " + t("buy_recommendation_none"))
        st.dataframe(
            df_watch[["ticker", "signal", "confidence", "rsi", "setup", "bucket", "prob_4pct_20d", "trades_20d"]],
            width="stretch",
            hide_index=True,
        )
        if failed_syms:
            st.caption("⚠️ " + ", ".join(failed_syms) + " niet geladen.")
    else:
        st.warning(t("watchlist_empty"))
        if failed_syms:
            st.caption("⚠️ " + ", ".join(failed_syms) + " niet geladen.")

elif page == "Optimizer":
    st.subheader(t("optimizer_title"))
    st.caption(t("optimizer_intro"))

    if st.button(t("optimizer_run_button")):
        try:
            # Basisdata en indicatoren één keer berekenen
            raw = fetch_data(ticker, outputsize=days + 600)
            base = raw.tail(days).reset_index(drop=True)
            base = add_indicators(base, rsi_period)
            base["confidence"] = compute_confidence(base)
            base["rsi_zone"] = base["rsi"].apply(lambda x: rsi_zone(float(x)))
            base["setup"] = base.apply(compute_setup_label, axis=1)

            # Rasters rond de huidige instellingen
            def _clamp(x, lo, hi):
                return max(lo, min(hi, x))

            buy_vals = sorted({round(_clamp(buy_threshold + d, 0.50, 0.95), 2) for d in [-0.05, 0.0, 0.05]})
            exit_vals = sorted({round(_clamp(exit_threshold + d, 0.10, 0.60), 2) for d in [-0.05, 0.0, 0.05]})
            hold_vals = sorted({int(_clamp(max_hold_days + d, 2, 180)) for d in [-5, 0, 5]})

            results = []
            for bt in buy_vals:
                for et in exit_vals:
                    for mh in hold_vals:
                        df_opt = base.copy()
                        df_opt["signal"] = (df_opt["confidence"] >= bt).map({True: "BUY", False: "HOLD"})
                        df_opt["conf_bucket"] = make_conf_buckets(df_opt["confidence"], b1, b2, b3)
                        trades_o, eq_o = run_backtest_equity_params(df_opt, et, mh)
                        if trades_o.empty:
                            continue
                        total_ret = eq_o["equity"].iloc[-1] - 1.0
                        max_dd_o = eq_o["drawdown"].min()
                        winrate_o = float((trades_o["return_pct"] > 0).mean())
                        trades_20d_o = trades_o[trades_o["days"] <= 20]
                        prob4_o = float("nan")
                        if not trades_20d_o.empty:
                            prob4_o = float((trades_20d_o["return_pct"] >= 0.04).mean())
                        results.append({
                            "buy_th": bt,
                            "exit_th": et,
                            "max_hold": mh,
                            "total_return": total_ret,
                            "max_drawdown": max_dd_o,
                            "winrate": winrate_o,
                            "prob_4pct_20d": prob4_o,
                            "trades": len(trades_o),
                        })

            if not results:
                st.warning(t("optimizer_no_results"))
            else:
                df_res = pd.DataFrame(results)
                df_res["_score"] = (
                    df_res["total_return"] * 100
                    - df_res["max_drawdown"].abs() * 50
                    + df_res["prob_4pct_20d"].fillna(0) * 20
                )
                df_res = df_res.sort_values("_score", ascending=False).drop(columns=["_score"])
                best = df_res.iloc[0]
                prob4_best = "n/a" if pd.isna(best["prob_4pct_20d"]) else f"{best['prob_4pct_20d']:.0%}"
                st.success(
                    t(
                        "optimizer_best_summary",
                        buy_th=best["buy_th"],
                        exit_th=best["exit_th"],
                        max_hold=int(best["max_hold"]),
                        total_return=best["total_return"],
                        max_drawdown=best["max_drawdown"],
                        winrate=best["winrate"],
                        prob4=prob4_best,
                        trades=int(best["trades"]),
                    )
                )
                st.caption(
                    t(
                        "optimizer_vs_current",
                        cur_buy=buy_threshold,
                        cur_exit=exit_threshold,
                        cur_hold=max_hold_days,
                    )
                )
                st.dataframe(df_res, width="stretch")
        except Exception as e:
            st.error(f"Optimizer error: {e}")

elif page == "Koopsignalen Gold":
    st.subheader(t("gold_title"))
    st.caption(t("gold_caption"))
    with st.expander(t("gold_expander")):
        st.markdown(t("gold_expander_text"))

    GOLD_SILVER = [
        ("GLD", t("gold_label")),
        ("SLV", t("silver_label")),
    ]

    try:
        col_gold, col_silver = st.columns(2)
        for (symbol, label), col in zip(GOLD_SILVER, [col_gold, col_silver]):
            with col:
                st.markdown(f"### {label} ({symbol})")
                try:
                    sdf = build_signal_df(symbol)
                    latest = sdf.iloc[-1]
                except Exception as e:
                    st.error(f"{t('error_load', symbol=symbol)} {e}")
                    continue

                signal_now = str(latest["signal"])
                conf_now = float(latest["confidence"])
                rsi_now = float(latest["rsi"])
                setup_now = str(latest["setup"])
                bucket_now = str(latest["conf_bucket"])
                ema20 = float(latest["ema20"])
                ema50 = float(latest["ema50"])
                ema200 = float(latest["ema200"])
                trend_short = "bullish" if ema20 > ema50 else "bearish"
                trend_long = "bullish" if ema50 > ema200 else "bearish"

                if signal_now == "BUY":
                    st.success(t("buy_signal_buy"))
                else:
                    st.warning(t("buy_signal_hold"))

                st.markdown(t("analysis"))
                st.markdown(f"- RSI({rsi_period}): {rsi_now:.1f} ({rsi_zone(rsi_now)})")
                st.markdown(f"- Trend: {trend_short} / {trend_long}")
                st.markdown(f"- Setup: {setup_now} · Bucket: {bucket_now}")
                st.markdown(f"- Confidence: {conf_now:.2f} ({t('threshold')} {buy_threshold})")

                if signal_now == "BUY":
                    st.markdown(t("advice_buy", symbol=symbol, conf=conf_now))
                else:
                    st.markdown(t("advice_hold", symbol=symbol))
                st.divider()

        # Samenvatting: welke van de twee heeft nu het sterkste signaal?
        rows = []
        for symbol, label in GOLD_SILVER:
            try:
                sdf = build_signal_df(symbol)
                r = sdf.iloc[-1]
                rows.append({"ticker": symbol, "naam": label, "signal": str(r["signal"]), "confidence": float(r["confidence"])})
            except Exception:
                continue
        if len(rows) >= 2:
            sum_df = pd.DataFrame(rows)
            sum_df["_rank"] = (sum_df["signal"] != "BUY").astype(int) * 1000 - sum_df["confidence"]
            sum_df = sum_df.sort_values("_rank").drop(columns=["_rank"])
            best = sum_df.iloc[0]
            st.info(t("best_of_two", ticker=best['ticker'], naam=best['naam'], signal=best['signal'], conf=best['confidence']))

    except Exception as e:
        st.error(f"{t('error_gold')} {e}")

elif page == "S&P 500":
    st.subheader(t("sp500_title"))
    st.caption(t("sp500_caption"))

    try:
        sdf = build_signal_df("SPY")
        latest = sdf.iloc[-1]

        # ---------- ANALYSE & KOOPSIGNAAL (SUMMARY) voor S&P 500 ----------
        st.divider()
        sp_signal = str(latest["signal"])
        sp_conf = float(latest["confidence"])
        sp_rsi = float(latest["rsi"])
        sp_setup = str(latest["setup"])
        sp_bucket = str(latest["conf_bucket"])
        sp_ema20 = float(latest["ema20"])
        sp_ema50 = float(latest["ema50"])
        sp_ema200 = float(latest["ema200"])
        sp_trend_short = "bullish" if sp_ema20 > sp_ema50 else "bearish"
        sp_trend_long = "bullish" if sp_ema50 > sp_ema200 else "bearish"

        if sp_signal == "BUY":
            st.success(t("summary_buy_box"))
        else:
            st.warning(t("summary_hold_box"))

        with st.expander(t("summary_expander"), expanded=True):
            st.caption(t("signal_basis_explanation"))
            st.markdown(t("summary_brief_analysis"))
            st.markdown(f"- **RSI({rsi_period}):** {sp_rsi:.1f} ({rsi_zone(sp_rsi)})")
            st.markdown(f"- **Trend:** {sp_trend_short} / {sp_trend_long}")
            st.markdown(f"- **Setup:** {sp_setup} · **Bucket:** {sp_bucket}")
            st.markdown(f"- **Confidence:** {sp_conf:.2f} ({t('threshold')} BUY = {buy_threshold})")
            if sp_signal == "BUY":
                st.markdown(t("advice_buy", symbol="SPY", conf=sp_conf))
            else:
                st.markdown(t("advice_hold", symbol="SPY"))

        st.divider()

        # Live signal voor SPY (korten metrics)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Signal", latest["signal"], help=t("signal_help"))
        c2.metric("Confidence", f"{latest['confidence']:.2f}", help=t("confidence_help"))
        c3.metric(f"RSI({rsi_period})", f"{latest['rsi']:.1f}", help=t("rsi_help"))
        c4.metric("Setup", str(latest["setup"]), help=t("setup_help"))
        c5.metric("Bucket", str(latest["conf_bucket"]), help=t("bucket_help"))

        st.caption(t("live_caption"))
        cols = [
            "date", "open", "high", "low", "close",
            "rsi", "ema20", "ema50", "ema200",
            "roc10", "range_pct",
            "confidence", "conf_bucket",
            "rsi_zone", "setup", "signal",
        ]
        st.dataframe(sdf[cols].sort_values("date", ascending=False).head(200), width="stretch")

        st.caption(t("chart_close"))
        st.line_chart(sdf.set_index("date")[["close"]], width="stretch")

    except Exception as e:
        st.error(f"{t('error_sp500')} {e}")

elif page == "Backtest":
    st.subheader(f"{t('page_backtest')} — {ticker}")
    with st.expander(t("backtest_expander")):
        st.markdown(t("backtest_expander_text"))
    try:
        df, trades, eq, stats = run_full_analysis(
            ticker, days, rsi_period, buy_threshold,
            exit_threshold, max_hold_days,
            b1, b2, b3
        )

        # Basic metrics
        total_return = eq["equity"].iloc[-1] - 1.0
        max_dd = eq["drawdown"].min()

        c1, c2, c3 = st.columns(3)
        c1.metric(t("total_return"), f"{total_return:.1%}", help=t("total_return_help"))
        c2.metric("Max drawdown", f"{max_dd:.1%}", help=t("max_dd_help"))
        c3.metric("Trades", f"{0 if trades.empty else len(trades)}", help=t("trades_help"))

        st.caption(t("equity_caption"))
        st.line_chart(eq.set_index("date")[["equity"]], width="stretch")

        st.caption(t("drawdown_caption"))
        st.line_chart(eq.set_index("date")[["drawdown"]], width="stretch")

        st.divider()
        st.subheader(t("trades_title"))
        if trades.empty:
            st.warning(t("no_trades_backtest"))
        else:
            show_cols = [
                "entry_date","entry_setup","entry_bucket","entry_confidence","entry_rsi_zone",
                "exit_date","days","return_pct"
            ]
            st.dataframe(trades.sort_values("entry_date", ascending=False)[show_cols].head(300), width="stretch")

        st.divider()
        st.subheader(t("d_conditional_title"))
        if stats.empty:
            st.warning(t("no_stats"))
        else:
            st.dataframe(stats, width="stretch")

            with st.expander(t("expectancy_expander")):
                st.markdown(t("expectancy_expander_text"))
            st.caption(t("interpretation"))

    except Exception as e:
        st.error(f"{t('error_backtest')} {e}")

elif page == "Export (later)":
    st.info(t("export_info"))
