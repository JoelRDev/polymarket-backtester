import requests
import questionary
import pandas as pd

def get_data():
    slug = input("Slug: ")
    interval = questionary.select(
        "Interval:",
        choices=["1h", "6h", "1d", "1w", "1m", "all", "max"]
    ).ask()

    url = "https://gamma-api.polymarket.com/markets"
    data = requests.get(url, params={"slug": slug}).json()

    if data:
        market = data[0]
    else:
        url = f"https://gamma-api.polymarket.com/events/slug/{slug}"
        event = requests.get(url).json()
        market = event["markets"][0]

    condition_id = market["conditionId"]

    url = f"https://clob.polymarket.com/clob-markets/{condition_id}"
    market_info = requests.get(url).json()

    selected_outcome = questionary.select(
        "Outcome:",
        choices=[questionary.Choice(title=outcome["o"], value=outcome)
        for outcome in market_info["t"]
        ]
    ).ask()

    token_id = selected_outcome["t"]

    params = {"market": token_id, "interval": interval} # TODO: Specify granularity
    data = requests.get("https://clob.polymarket.com/prices-history", params=params).json()

    history_df = pd.DataFrame(data["history"])
    return history_df