# Polymarket Backtester

A small Python backtesting project for experimenting with simple Polymarket trading strategies against historical price data.

The project fetches market history from Polymarket, asks the user to select a market outcome, runs a strategy over the returned price series, and reports realized/unrealized PnL, equity, orders, trades, and ranked trade results.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The program prompts for:

- `Slug`: a Polymarket market or event slug.
- `Interval`: one of `1h`, `6h`, `1d`, `1w`, `1m`, `all`, or `max`.
- `Outcome`: the outcome token to backtest.
- `Initial capital`: starting cash for the simulation.

## Architecture

```text
main.py
  -> data_setup.get_data()
  -> backtester.backtester(data)
       -> strategy.strategy(...)
       -> models.Order
       -> models.Position
```

### `main.py`

The application entry point. It loads historical market data, passes it into the backtester, and prints the resulting performance dictionary.

### `data_setup.py`

Handles user input and Polymarket data retrieval.

The data flow is:

1. Look up the provided slug using the Gamma markets API.
2. If no market is found, treat the slug as an event slug and use the first market from that event.
3. Fetch CLOB market metadata using the market condition ID.
4. Ask the user which outcome token to test.
5. Fetch historical price data from the CLOB `prices-history` endpoint.
6. Return the history as a pandas `DataFrame`.

### `strategy.py`

Contains the strategy function used by the backtester.

Current strategy contract:

```python
def strategy(time, price, capital, long_position, short_position):
    return [Order(price, quantity, direction)]
```

The strategy receives the current timestamp, current YES price, available capital, and remaining long/short position sizes. It returns a list of `Order` objects.

Order behavior:

- `direction="LONG"` buys or sells the selected YES outcome.
- `direction="SHORT"` buys or sells the inverse side, priced as `1 - yes_price`.
- Positive `quantity` opens or increases a position.
- Negative `quantity` closes an existing position.

The included sample strategy buys 50 LONG shares when the selected outcome price is below `0.4`.

### `backtester.py`

Controls the simulation loop, matching model, cash accounting, and position tracking.

For each historical price row, it:

1. Calls `strategy(...)`.
2. Validates each order direction and quantity.
3. Converts LONG/SHORT directions into the correct simulated fill price.
4. Opens positions for positive quantities when enough cash is available.
5. Closes positions for negative quantities when enough position size is available.
6. Tracks orders, trades, realized PnL, unrealized PnL, final equity, cash, and remaining positions.

The matching model is intentionally simple: orders are filled immediately at the historical price for LONG positions, or `1 - price` for SHORT positions. It does not simulate queue priority, spread, slippage, partial fills from market depth, fees, or liquidity constraints.

### `models.py`

Defines the core domain objects:

- `Order`: a requested trade with price, quantity, and direction.
- `Position`: average-entry position accounting with add, close, market value, realized PnL, and unrealized PnL helpers.

## Output

`backtester(...)` returns a dictionary containing:

- `realized_pnl`
- `unrealized_pnl`
- `final_equity`
- `total_pnl`
- `orders`
- `trades`
- `ranked_trades`
- `cash`
- `remaining_long_position`
- `remaining_short_position`
- `long_average_entry_price`
- `short_average_entry_price`

## Limitations

This backtester uses Polymarket historical price data, not historical order book snapshots.

Polymarket does not provide historical order book access through the endpoints used by this project. As a result, the backtester cannot reconstruct bid/ask depth, available liquidity, queue position, historical spreads, or whether a real market order of a given size would have filled at the simulated price.

Because of this, results should be treated as approximate strategy research, not execution-accurate performance.

Other current limitations:

- No trading fees.
- No slippage model.
- No liquidity or market-depth checks.
- No partial fills.
- No explicit resolution/payout handling.
- Event slugs default to the first market in the event response.

## Extending

To test a new strategy, edit `strategy.py` and return one or more `Order` objects from `strategy(...)`.

For example:

```python
from models import Order

def strategy(time, price, capital, long_position, short_position):
    orders = []

    if price < 0.35 and capital >= price * 25:
        orders.append(Order(price, 25, "LONG"))

    if price > 0.65 and long_position >= 25:
        orders.append(Order(price, -25, "LONG"))

    return orders
```
