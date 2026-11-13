# TR-AUTO — Alpaca Paper connection bootstrap

**Status: read-only connection checker only; NOT a trading bot or ChatGPT plugin.**

This repository is the target for the TR-AUTO project. The research reference is [TradingAgents](https://github.com/TauricResearch/TradingAgents), inspected at commit 9fa1196fffbcfd9de5146d2dd2869df84ab99838. This starter does not copy or replace the upstream framework.

See [MVP dashboard task](https://github.com/mytest19861986/tr-auto/issues/1) and [Paper Trading integration task](https://github.com/mytest19861986/tr-auto/issues/2).

## Security and local startup

- Current code makes only a read-only GET to https://paper-api.alpaca.markets/v2/account, on a hardcoded paper endpoint. There is no order-placement function, scheduler, live trading, or brokerage write capability.
- **Never paste your Alpaca API key or secret into chat, GitHub, issues, code or commits.** Run the CLI on your own machine and enter them using hidden prompts, or configure ALPACA_PAPER_KEY_ID and ALPACA_PAPER_SECRET_KEY in your local process environment/secret manager. This program does not save credentials.
- No account number, balance, full API response or credentials are printed.

Requirements: Python 3.11+ (standard library only). From the repository root:

~~~sh
python -m unittest discover -s tests -v
python -m tr_auto.paper_healthcheck
~~~

Second command checks connection only; **no trade is executed**. Test suite uses fake data and does not call Alpaca.

## Owner-approved limits for eventual order executor

- At most **30 USD simulated notional** for each new position.
- At most **4 concurrent positions** across US stocks and crypto, counting reserved slots for pending entries.
- **10 calendar days** initial evaluation from first verified active experiment.
- Eligible US-equity shorts may be implemented with broker account, share eligibility and size checks. **Crypto spot shorts are not supported** on Alpaca. Bearish crypto signals can be logged but must not be labeled as executed short trades.
- Trading and order management must stay OFF until the full execution adapter is separately built, tested and the admin enables paper ordering. Nothing in this starter authorizes orders.

## Remaining work

Implement TradingAgents signal ingestion, idempotent paper-only order adapter and reconciliation, fee-aware matched realized P&L and daily win rates, local admin dashboard with authentication, and an optional secure custom MCP plugin (subject to account/workspace access). Localhost by itself cannot be accessed directly from ChatGPT; a supported secure tunnel or HTTPS endpoint plus explicit plugin connection is needed.

No broker credentials, connection success, orders, performance numbers or owner-visible runtime are claimed at this stage.
