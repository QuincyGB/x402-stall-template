# x402-stall-template — a stall in a box

Start a paid x402 micro-service ("stall") on Base in an afternoon.
This template distills the rails the **Verdict Row** fleet runs in
production (Token Verdict, RouteVerdict, ListSmith, StallRow,
LockSmith — five services, 20+ paid routes, settled traffic on CDP
and PayAI) into a minimal, copyable starting point.

You get:

| Piece | File | What it does |
|---|---|---|
| Paywall middleware | `app/paywall.py` | x402 v2 `exact` on Base via the official SDK; unpaid calls get a 402 whose accepts carry your price and payTo |
| Pack accounting | `app/packs.py` | Prepaid credit packs in sqlite: idempotent mint (a re-presented payment never mints twice), atomic debit, free balance reads, exhausted → 402 / expired → 410, **no silent per-call fallback** |
| Freshness guard | `app/freshness.py` | Refuse to serve from a stale snapshot: paid routes 502 before settlement, subscription cycles skip with no debit |
| Discovery generator | `app/discovery.py` | One route table → `/.well-known/x402` manifest + a full Bazaar extension per route (typed output schema, example ≤ ~1.5 KB) |
| Example stall | `app/main.py` | `POST /v1/word-count` ($0.01) + pack buy/balance, `/health`, landing page |
| Keepalive | `scripts/keepalive.py` | Health watchdog: probes `/health`, logs, non-zero exit on a failure streak — run it from cron |
| Listing checklist | `checks/listsmith-ci.md` | The pre-listing checks the fleet's own listings are graded against (description, schemas, examples, live-402 match) |

## Quickstart

```bash
cp .env.example .env    # set X402_PAY_TO to your Base address
pip install -r requirements.txt
uvicorn app.main:app --port 8402
curl -X POST localhost:8402/v1/word-count -H 'Content-Type: application/json' \
     -d '{"text":"hello stall"}'      # -> 402 with your price + payTo
curl localhost:8402/.well-known/x402  # -> your discovery manifest
```

Buyers pay with any x402 client. For *your own* loops and agents,
the fleet's defaults are:

- **x402-guard** (PyPI `x402-guard`, npm `@quincygb/x402-guard`) —
  buyer-side middleware: budget caps, payTo pinning, pack spending.
- **x402-loop-kits** (github.com/QuincyGB/x402-loop-kits) — monitor /
  pre-trade / inspector loop templates, plus the Managed Loop and
  Verdict Index publications this template's patterns come from.

## The rules baked in (learned in production, steal them)

1. **Never charge for undelivered data.** An upstream failure returns
   502; the middleware settles only on success.
2. **Build the payment middleware once.** Constructing it fetches the
   facilitator's `/supported` document — per-request construction
   taxes every call, including health checks.
3. **Descriptions under 500 chars, with a "Use this when…" sentence.**
   The CDP catalog enforces the limit at indexing time, silently.
4. **Examples are small.** Settled-style indexers drop listing
   samples over ~1.5 KB; keep output examples compact.
5. **State that must survive deploys lives on a mounted volume,**
   and `/health` says which mode is live (`storage` block).
6. **Packs never fall back.** An exhausted pack returns 402 and an
   expired one 410 — never a surprise per-call charge.
7. **Name every rail you accept, in the description.** Every route
   description ends with the payable clause for the stall's rails
   (`app/discovery.py`: `PAYABLE_CLAUSES`, driven by the `RAILS`
   constant — "Payable in USDC on Base or Solana." for a dual-accept
   stall). Buyers and indexers read descriptions to learn how they
   can pay; a rail the description doesn't mention is a rail nobody
   uses. Keep `RAILS` honest: it must match the accepts your 402
   actually carries.
8. **Snapshot products refuse stale data.** If a route serves from
   a periodically refreshed snapshot (a catalog diff, an alert
   feed, a watchlist), guard it with `app/freshness.py`: a paid
   route answers 502 *before* settlement when the snapshot is older
   than its cadence, and a subscription cycle skips with no debit.
   Serving stale data as current is worse than an error — buyers
   act on it.

## Facilitator choice = catalog choice

`X402_FACILITATOR_URL` decides which index a settled payment feeds:
CDP (`https://api.cdp.coinbase.com/platform/v2/x402`, needs CDP API
keys) feeds the Bazaar catalog; PayAI
(`https://facilitator.payai.network`) feeds the PayAI index; the
keyless default settles on Base but feeds neither. One deployment
settles through one facilitator at a time — appear in both indexes
by settling at least one call under each configuration.

## License

MIT. Built by Verdict Row; run your own stall anywhere.
