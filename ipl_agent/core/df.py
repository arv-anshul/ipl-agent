from functools import lru_cache

import polars as pl

from ipl_agent.settings import settings


def preprocess_df(df: pl.LazyFrame) -> pl.LazyFrame:
    teams_abbr = {
        "Chennai Super Kings": "CSK",
        "Deccan Chargers": "SRH",
        "Delhi Capitals": "DC",
        "Delhi Daredevils": "DC",
        "Gujarat Lions": "GT",
        "Gujarat Titans": "GT",
        "Kings XI Punjab": "PBKS",
        "Kochi Tuskers Kerala": "SRH",
        "Kolkata Knight Riders": "KKR",
        "Lucknow Super Giants": "LSG",
        "Mumbai Indians": "MI",
        "Pune Warriors": "CSK",
        "Punjab Kings": "PBKS",
        "Rajasthan Royals": "RR",
        "Rising Pune Supergiant": "CSK",
        "Rising Pune Supergiants": "CSK",
        "Royal Challengers Bangalore": "RCB",
        "Royal Challengers Bengaluru": "RCB",
        "Sunrisers Hyderabad": "SRH",
    }

    return df.with_columns(
        pl.col("team1", "team2", "winner", "toss_winner").replace_strict(
            teams_abbr,
            default="NA",
            return_dtype=pl.String,
        ),
    )


@lru_cache(1)
def load_dataframe() -> pl.DataFrame:
    ipl_matches = (
        pl.scan_csv(
            settings.IPL_MATCHES_DATA_URL.unicode_string(),
            ignore_errors=True,
        )
        .select(
            "season",
            "city",
            "venue",
            "player_of_match",
            "team1",
            "team2",
            "toss_winner",
            "toss_decision",
            "target_runs",
            "winner",
        )
        .pipe(preprocess_df)
        .collect()
    )
    return ipl_matches
