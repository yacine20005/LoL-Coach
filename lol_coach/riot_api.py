import time

import requests


def build_headers(api_key):
    return {"X-Riot-Token": api_key}


def get_puuid(game_name, tag_line, headers, region_routing="europe"):
    account_url = (
        f"https://{region_routing}.api.riotgames.com/riot/account/v1/accounts"
        f"/by-riot-id/{game_name}/{tag_line}"
    )
    response = requests.get(account_url, headers=headers, timeout=10)
    if response.status_code == 200:
        account_data = response.json()
        return account_data["puuid"]
    raise requests.exceptions.RequestException(
        f"Error fetching PUUID: {response.status_code} - {response.text}"
    )


def get_match_ids(
    puuid,
    headers,
    total_games=300,
    batch_size=100,
    region_routing="europe",
    sleep_seconds=1.0,
):
    match_id_list = []
    start = 0

    while len(match_id_list) < total_games:
        url = (
            f"https://{region_routing}.api.riotgames.com/lol/match/v5/matches"
            f"/by-puuid/{puuid}/ids?start={start}&count={batch_size}"
        )
        response = requests.get(url, headers=headers, timeout=10)
        response_json = response.json()

        if not response_json:
            break

        match_id_list.extend(response_json)
        start += batch_size
        time.sleep(sleep_seconds)

    return match_id_list[:total_games]


def fetch_match_info(match_id, headers, region_routing="europe"):
    match_url = f"https://{region_routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    try:
        response = requests.get(match_url, headers=headers, timeout=10)
        response.raise_for_status()
        match_data = response.json()
        info = match_data.get("info")
        if info is None:
            print(f"  Warning: No 'info' in match data for {match_id}")
            return None
        return info
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching match {match_id}: {e}")
        return None
    except (ValueError, KeyError, TypeError) as e:
        print(f"  Unexpected error processing {match_id}: {e}")
        return None
