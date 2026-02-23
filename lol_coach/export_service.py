import time

import pandas as pd
from py_toon_format import encode

from .match_processing import build_game_record, find_player_participant
from .riot_api import fetch_match_info


def process_match(
    match_id,
    index,
    total_matches,
    puuid,
    headers,
    region_routing="europe",
):
    print(f"Processing match {index}/{total_matches}: {match_id}")
    info = fetch_match_info(match_id, headers, region_routing=region_routing)
    if info is None:
        return None

    participant = find_player_participant(info, puuid)
    if participant is None:
        return None

    duration = info.get("gameDuration")
    if not duration:
        return None

    try:
        return build_game_record(participant, duration)
    except (KeyError, TypeError, ValueError) as e:
        print(f"  Error processing participant data for match {match_id}: {e}")
        return None


def collect_games_data(
    match_ids,
    puuid,
    headers,
    region_routing="europe",
    sleep_seconds=1.5,
):
    games_data = []
    total_matches = len(match_ids)

    for index, match_id in enumerate(match_ids, start=1):
        game_record = process_match(
            match_id,
            index,
            total_matches,
            puuid,
            headers,
            region_routing=region_routing,
        )
        if game_record is not None:
            games_data.append(game_record)
        time.sleep(sleep_seconds)

    return games_data


def export_tabular_files(games_data, game_name, tag_line):
    base_name = f"recent_games_{game_name}_{tag_line}"
    df = pd.DataFrame(games_data)
    df.to_csv(f"{base_name}.csv", index=False)
    df.to_json(f"{base_name}.json", orient="records", indent=2)


def export_toon_file(games_data, game_name, tag_line):
    try:
        toon = encode(games_data)
        if isinstance(toon, str):
            toon = toon.encode("utf-8")
        with open(f"recent_games_{game_name}_{tag_line}.txt", "wb") as file_handle:
            file_handle.write(toon)
        print("Toon format export successful.")
    except (ValueError, TypeError, OSError, UnicodeEncodeError) as e:
        print(f"Warning: Could not export toon format: {e}")
