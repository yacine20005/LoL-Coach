import time
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from py_toon_format import encode

load_dotenv()


def get_required_env_var(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_int_env_var(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {name}: {value}") from exc


API_KEY = get_required_env_var("RIOT_API_KEY")
GAME_NAME = get_required_env_var("EXPORT_GAME_NAME")
TAG_LINE = get_required_env_var("EXPORT_TAG_LINE")
TOTAL_GAMES = get_int_env_var("EXPORT_TOTAL_GAMES", 100)


def build_headers(api_key):
    return {"X-Riot-Token": api_key}


def get_puuid(game_name, tag_line, headers):
    account_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    response = requests.get(account_url, headers=headers)
    if response.status_code == 200:
        account_data = response.json()
        return account_data["puuid"]
    raise Exception(f"Error fetching PUUID: {response.status_code} - {response.text}")


def get_match_ids(puuid, headers, total_games=300, batch_size=100):
    match_ids = []
    start = 0

    while len(match_ids) < total_games:
        url = (
            f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
            f"?start={start}&count={batch_size}"
        )
        response = requests.get(url, headers=headers)
        batch = response.json()

        if not batch:
            break

        match_ids.extend(batch)
        start += batch_size
        time.sleep(1)

    return match_ids[:total_games]


def fetch_match_info(match_id, headers):
    match_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    try:
        response = requests.get(match_url, headers=headers)
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
    except Exception as e:
        print(f"  Unexpected error processing {match_id}: {e}")
        return None


def find_player_participant(info, puuid):
    for participant in info.get("participants", []):
        if participant.get("puuid") == puuid:
            return participant
    return None


def compute_core_metrics(participant, duration):
    kills = participant["kills"]
    assists = participant["assists"]
    deaths = participant["deaths"]
    kda = (kills + assists) / max(1, deaths)

    cs = participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]
    cs_per_min = cs / (duration / 60)

    return {
        "kda": round(kda, 2),
        "cs": cs,
        "cs_per_min": round(cs_per_min, 2),
    }


def extract_items(participant):
    return [participant.get(f"item{i}", 0) for i in range(7)]


def build_game_record(participant, duration):
    metrics = compute_core_metrics(participant, duration)
    items = extract_items(participant)
    challenges = participant.get("challenges", {})

    return {
        "champion": participant["championName"],
        "role": participant["role"],
        "lane": participant["lane"],
        "team_position": participant.get("teamPosition", ""),
        "individual_position": participant.get("individualPosition", ""),
        "win": participant["win"],
        "kills": participant["kills"],
        "deaths": participant["deaths"],
        "assists": participant["assists"],
        "kda": metrics["kda"],
        "cs": metrics["cs"],
        "cs_per_min": metrics["cs_per_min"],
        "gold": participant["goldEarned"],
        "gold_spent": participant.get("goldSpent", 0),
        "damage_dealt": participant["totalDamageDealtToChampions"],
        "damage_dealt_to_objectives": participant.get("damageDealtToObjectives", 0),
        "damage_dealt_to_buildings": participant.get("damageDealtToBuildings", 0),
        "physical_damage_dealt": participant.get("physicalDamageDealt", 0),
        "magic_damage_dealt": participant.get("magicDamageDealt", 0),
        "true_damage_dealt": participant.get("trueDamageDealt", 0),
        "physical_damage_to_champs": participant.get("physicalDamageDealtToChampions", 0),
        "magic_damage_to_champs": participant.get("magicDamageDealtToChampions", 0),
        "true_damage_to_champs": participant.get("trueDamageDealtToChampions", 0),
        "damage_taken": participant["totalDamageTaken"],
        "physical_damage_taken": participant.get("physicalDamageTaken", 0),
        "magic_damage_taken": participant.get("magicDamageTaken", 0),
        "true_damage_taken": participant.get("trueDamageTaken", 0),
        "damage_self_mitigated": participant.get("damageSelfMitigated", 0),
        "total_heal": participant["totalHeal"],
        "total_heal_on_teammates": participant.get("totalHealsOnTeammates", 0),
        "damage_shielded_on_teammates": participant.get("totalDamageShieldedOnTeammates", 0),
        "total_cc_dealt": participant.get("timeCCingOthers", 0),
        "total_time_cc_dealt": participant.get("totalTimeCCDealt", 0),
        "vision_score": participant["visionScore"],
        "wards_placed": participant["wardsPlaced"],
        "wards_killed": participant.get("wardsKilled", 0),
        "sight_wards_bought": participant.get("sightWardsBoughtInGame", 0),
        "vision_wards_bought": participant.get("visionWardsBoughtInGame", 0),
        "detector_wards_placed": participant.get("detectorWardsPlaced", 0),
        "pentakills": participant.get("pentaKills", 0),
        "quadrakills": participant.get("quadraKills", 0),
        "triplekills": participant.get("tripleKills", 0),
        "doublekills": participant.get("doubleKills", 0),
        "multikills": participant.get("largestMultiKill", 0),
        "dragon_kills": participant.get("dragonKills", 0),
        "baron_kills": participant.get("baronKills", 0),
        "turret_kills": participant.get("turretKills", 0),
        "turret_takedowns": participant.get("turretTakedowns", 0),
        "turrets_lost": participant.get("turretsLost", 0),
        "inhibitor_kills": participant.get("inhibitorKills", 0),
        "inhibitor_takedowns": participant.get("inhibitorTakedowns", 0),
        "inhibitors_lost": participant.get("inhibitorsLost", 0),
        "nexus_kills": participant.get("nexusKills", 0),
        "nexus_takedowns": participant.get("nexusTakedowns", 0),
        "total_ally_jungle_minions": participant.get("totalAllyJungleMinionsKilled", 0),
        "total_enemy_jungle_minions": participant.get("totalEnemyJungleMinionsKilled", 0),
        "true_mitigated_damage": participant.get("damageSelfMitigated", 0),
        "longest_time_alive": participant.get("longestTimeSpentLiving", 0),
        "total_time_dead": participant.get("totalTimeSpentDead", 0),
        "killing_sprees": participant.get("killingSprees", 0),
        "largest_killing_spree": participant.get("largestKillingSpree", 0),
        "first_blood_kill": participant.get("firstBloodKill", False),
        "first_blood_assist": participant.get("firstBloodAssist", False),
        "first_tower_kill": participant.get("firstTowerKill", False),
        "first_tower_assist": participant.get("firstTowerAssist", False),
        "champ_level": participant.get("champLevel", 0),
        "champ_experience": participant.get("champExperience", 0),
        "summoner1_id": participant.get("summoner1Id", 0),
        "summoner2_id": participant.get("summoner2Id", 0),
        "summoner1_casts": participant.get("summoner1Casts", 0),
        "summoner2_casts": participant.get("summoner2Casts", 0),
        "spell1_casts": participant.get("spell1Casts", 0),
        "spell2_casts": participant.get("spell2Casts", 0),
        "spell3_casts": participant.get("spell3Casts", 0),
        "spell4_casts": participant.get("spell4Casts", 0),
        "item0": items[0],
        "item1": items[1],
        "item2": items[2],
        "item3": items[3],
        "item4": items[4],
        "item5": items[5],
        "item6": items[6],
        "items_purchased": participant.get("itemsPurchased", 0),
        "consumables_purchased": participant.get("consumablesPurchased", 0),
        "bounce_level": participant.get("bountyLevel", 0),
        "unrealized_kills": participant.get("unrealKills", 0),
        "time_played": participant.get("timePlayed", 0),
        "game_ended_in_surrender": participant.get("gameEndedInSurrender", False),
        "game_ended_in_early_surrender": participant.get("gameEndedInEarlySurrender", False),
        "team_early_surrendered": participant.get("teamEarlySurrendered", False),
        "gold_per_minute": round(challenges.get("goldPerMinute", 0), 2),
        "damage_per_minute": round(challenges.get("damagePerMinute", 0), 2),
        "vision_score_per_minute": round(challenges.get("visionScorePerMinute", 0), 2),
        "kill_participation": round(challenges.get("killParticipation", 0), 3),
        "kda_challenge": round(challenges.get("kda", 0), 2),
        "largest_critical_strike": participant.get("largestCriticalStrike", 0),
        "damage_taken_on_team_percentage": round(challenges.get("damageTakenOnTeamPercentage", 0), 3),
        "max_level_lead_lane_opponent": challenges.get("maxLevelLeadLaneOpponent", 0),
        "max_cs_advantage_on_lane_opponent": round(challenges.get("maxCsAdvantageOnLaneOpponent", 0), 2),
        "takedowns": challenges.get("takedowns", 0),
        "takedowns_first_25_minutes": challenges.get("takedownsFirst25Minutes", 0),
        "deaths_by_enemy_champs": challenges.get("deathsByEnemyChamps", 0),
        "enemy_champ_immobilizations": challenges.get("enemyChampionImmobilizations", 0),
        "solo_kills": challenges.get("soloKills", 0),
        "outnumbered_kills": challenges.get("outnumberedKills", 0),
        "game_duration": duration,
    }


def process_match(match_id, index, total_matches, puuid, headers):
    print(f"Processing match {index}/{total_matches}: {match_id}")
    info = fetch_match_info(match_id, headers)
    if info is None:
        return None

    participant = find_player_participant(info, puuid)
    if participant is None:
        return None

    duration = info["gameDuration"]
    try:
        return build_game_record(participant, duration)
    except Exception as e:
        print(f"  Error processing participant data for match {match_id}: {e}")
        return None


def collect_games_data(match_ids, puuid, headers):
    games_data = []
    total_matches = len(match_ids)

    for index, match_id in enumerate(match_ids, start=1):
        game_record = process_match(match_id, index, total_matches, puuid, headers)
        if game_record is not None:
            games_data.append(game_record)
        time.sleep(1.5)

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
    except Exception as e:
        print(f"Warning: Could not export toon format: {e}")


def run_export(game_name, tag_line, total_games):
    headers = build_headers(API_KEY)

    puuid = get_puuid(game_name, tag_line, headers)
    print(f"PUUID for {game_name}#{tag_line}: {puuid}")

    match_ids = get_match_ids(puuid, headers, total_games=total_games)
    print(f"Found {len(match_ids)} recent matches for {game_name}#{tag_line}.")

    games_data = collect_games_data(match_ids, puuid, headers)
    export_tabular_files(games_data, game_name, tag_line)
    export_toon_file(games_data, game_name, tag_line)

    print(f"Export completed for {game_name}#{tag_line}. ({len(games_data)} games exported)")


def main():
    run_export(GAME_NAME, TAG_LINE, TOTAL_GAMES)


if __name__ == "__main__":
    main()