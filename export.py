import requests
import pandas as pd
import time
from py_toon_format import encode, decode

API_KEY = "RGAPI-54e324a8-9946-4529-bfae-dbf5d576af51"
GAME_NAME = "Malaxeur2Milf"
TAG_LINE = "92i"

headers = {"X-Riot-Token": API_KEY}

def get_match_ids(puuid, total_games=300):
    match_ids = []
    start = 0
    
    while len(match_ids) < total_games:
        url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count=100"
        response = requests.get(url, headers=headers)
        batch = response.json()
        
        if not batch:
            break
            
        match_ids.extend(batch)
        start += 100
        time.sleep(1)

    return match_ids[:total_games]

# Get puuid
account_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{GAME_NAME}/{TAG_LINE}"
account_data = requests.get(account_url, headers=headers).json()
puuid = account_data["puuid"]
print(f"PUUID for {GAME_NAME}#{TAG_LINE}: {puuid}")

# Get recent matches id
match_ids = get_match_ids(puuid, total_games=100)
print(f"Found {len(match_ids)} recent matches for {GAME_NAME}#{TAG_LINE}.")

games_data = []
counter = 0

for match_id in match_ids:
    match_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    print(f"Processing match {counter + 1}/{len(match_ids)}: {match_id}")
    counter += 1
    
    try:
        response = requests.get(match_url, headers=headers)
        response.raise_for_status()
        match_data = response.json()
        
        if "info" not in match_data:
            print(f"  Warning: No 'info' in match data for {match_id}")
            continue
            
        info = match_data["info"]
        duration = info["gameDuration"]
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching match {match_id}: {e}")
        continue
    except Exception as e:
        print(f"  Unexpected error processing {match_id}: {e}")
        continue

    for p in info["participants"]:
        if p["puuid"] == puuid:
            try:
                kda = (p["kills"] + p["assists"]) / max(1, p["deaths"])
                cs = p["totalMinionsKilled"] + p["neutralMinionsKilled"]
                cs_per_min = cs / (duration / 60)
                
                # Items
                items = [p.get(f"item{i}", 0) for i in range(7)]
                
                # Challenges data
                challenges = p.get("challenges", {})
                
                # Perks (runes)
                perks = p.get("perks", {})

                games_data.append({
                    "champion": p["championName"],
                    "role": p["role"],
                    "lane": p["lane"],
                    "team_position": p.get("teamPosition", ""),
                    "individual_position": p.get("individualPosition", ""),
                    "win": p["win"],
                    "kills": p["kills"],
                    "deaths": p["deaths"],
                    "assists": p["assists"],
                    "kda": round(kda, 2),
                    "cs": cs,
                    "cs_per_min": round(cs_per_min, 2),
                    "gold": p["goldEarned"],
                    "gold_spent": p.get("goldSpent", 0),
                    "damage_dealt": p["totalDamageDealtToChampions"],
                    "damage_dealt_to_objectives": p.get("damageDealtToObjectives", 0),
                    "damage_dealt_to_buildings": p.get("damageDealtToBuildings", 0),
                    "physical_damage_dealt": p.get("physicalDamageDealt", 0),
                    "magic_damage_dealt": p.get("magicDamageDealt", 0),
                    "true_damage_dealt": p.get("trueDamageDealt", 0),
                    "physical_damage_to_champs": p.get("physicalDamageDealtToChampions", 0),
                    "magic_damage_to_champs": p.get("magicDamageDealtToChampions", 0),
                    "true_damage_to_champs": p.get("trueDamageDealtToChampions", 0),
                    "damage_taken": p["totalDamageTaken"],
                    "physical_damage_taken": p.get("physicalDamageTaken", 0),
                    "magic_damage_taken": p.get("magicDamageTaken", 0),
                    "true_damage_taken": p.get("trueDamageTaken", 0),
                    "damage_self_mitigated": p.get("damageSelfMitigated", 0),
                    "total_heal": p["totalHeal"],
                    "total_heal_on_teammates": p.get("totalHealsOnTeammates", 0),
                    "damage_shielded_on_teammates": p.get("totalDamageShieldedOnTeammates", 0),
                    "total_cc_dealt": p.get("timeCCingOthers", 0),
                    "total_time_cc_dealt": p.get("totalTimeCCDealt", 0),
                    "vision_score": p["visionScore"],
                    "wards_placed": p["wardsPlaced"],
                    "wards_killed": p.get("wardsKilled", 0),
                    "sight_wards_bought": p.get("sightWardsBoughtInGame", 0),
                    "vision_wards_bought": p.get("visionWardsBoughtInGame", 0),
                    "detector_wards_placed": p.get("detectorWardsPlaced", 0),
                    "pentakills": p.get("pentaKills", 0),
                    "quadrakills": p.get("quadraKills", 0),
                    "triplekills": p.get("tripleKills", 0),
                    "doublekills": p.get("doubleKills", 0),
                    "multikills": p.get("largestMultiKill", 0),
                    "dragon_kills": p.get("dragonKills", 0),
                    "baron_kills": p.get("baronKills", 0),
                    "turret_kills": p.get("turretKills", 0),
                    "turret_takedowns": p.get("turretTakedowns", 0),
                    "turrets_lost": p.get("turretsLost", 0),
                    "inhibitor_kills": p.get("inhibitorKills", 0),
                    "inhibitor_takedowns": p.get("inhibitorTakedowns", 0),
                    "inhibitors_lost": p.get("inhibitorsLost", 0),
                    "nexus_kills": p.get("nexusKills", 0),
                    "nexus_takedowns": p.get("nexusTakedowns", 0),
                    "total_ally_jungle_minions": p.get("totalAllyJungleMinionsKilled", 0),
                    "total_enemy_jungle_minions": p.get("totalEnemyJungleMinionsKilled", 0),
                    "true_mitigated_damage": p.get("damageSelfMitigated", 0),
                    "longest_time_alive": p.get("longestTimeSpentLiving", 0),
                    "total_time_dead": p.get("totalTimeSpentDead", 0),
                    "killing_sprees": p.get("killingSprees", 0),
                    "largest_killing_spree": p.get("largestKillingSpree", 0),
                    "first_blood_kill": p.get("firstBloodKill", False),
                    "first_blood_assist": p.get("firstBloodAssist", False),
                    "first_tower_kill": p.get("firstTowerKill", False),
                    "first_tower_assist": p.get("firstTowerAssist", False),
                    "champ_level": p.get("champLevel", 0),
                    "champ_experience": p.get("champExperience", 0),
                    "summoner1_id": p.get("summoner1Id", 0),
                    "summoner2_id": p.get("summoner2Id", 0),
                    "summoner1_casts": p.get("summoner1Casts", 0),
                    "summoner2_casts": p.get("summoner2Casts", 0),
                    "spell1_casts": p.get("spell1Casts", 0),
                    "spell2_casts": p.get("spell2Casts", 0),
                    "spell3_casts": p.get("spell3Casts", 0),
                    "spell4_casts": p.get("spell4Casts", 0),
                    "item0": items[0],
                    "item1": items[1],
                    "item2": items[2],
                    "item3": items[3],
                    "item4": items[4],
                    "item5": items[5],
                    "item6": items[6],
                    "items_purchased": p.get("itemsPurchased", 0),
                    "consumables_purchased": p.get("consumablesPurchased", 0),
                    "bounce_level": p.get("bountyLevel", 0),
                    "unrealized_kills": p.get("unrealKills", 0),
                    "time_played": p.get("timePlayed", 0),
                    "game_ended_in_surrender": p.get("gameEndedInSurrender", False),
                    "game_ended_in_early_surrender": p.get("gameEndedInEarlySurrender", False),
                    "team_early_surrendered": p.get("teamEarlySurrendered", False),
                    # Challenges
                    "gold_per_minute": round(challenges.get("goldPerMinute", 0), 2),
                    "damage_per_minute": round(challenges.get("damagePerMinute", 0), 2),
                    "vision_score_per_minute": round(challenges.get("visionScorePerMinute", 0), 2),
                    "kill_participation": round(challenges.get("killParticipation", 0), 3),
                    "kda_challenge": round(challenges.get("kda", 0), 2),
                    "largest_critical_strike": p.get("largestCriticalStrike", 0),
                    "damage_taken_on_team_percentage": round(challenges.get("damageTakenOnTeamPercentage", 0), 3),
                    "max_level_lead_lane_opponent": challenges.get("maxLevelLeadLaneOpponent", 0),
                    "max_cs_advantage_on_lane_opponent": round(challenges.get("maxCsAdvantageOnLaneOpponent", 0), 2),
                    "takedowns": challenges.get("takedowns", 0),
                    "takedowns_first_25_minutes": challenges.get("takedownsFirst25Minutes", 0),
                    "deaths_by_enemy_champs": challenges.get("deathsByEnemyChamps", 0),
                    "enemy_champ_immobilizations": challenges.get("enemyChampionImmobilizations", 0),
                    "solo_kills": challenges.get("soloKills", 0),
                    "outnumbered_kills": challenges.get("outnumberedKills", 0),
                    "game_duration": duration
                })
            except Exception as e:
                print(f"  Error processing participant data for match {match_id}: {e}")
                continue

    time.sleep(1.5)  # Increased to avoid rate limiting

df = pd.DataFrame(games_data)
df.to_csv(f"recent_games_{GAME_NAME}_{TAG_LINE}.csv", index=False)
df.to_json(f"recent_games_{GAME_NAME}_{TAG_LINE}.json", orient="records", indent=2)

try:
    toon = encode(games_data)
    # Ensure toon is bytes
    if isinstance(toon, str):
        toon = toon.encode('utf-8')
    with open(f"recent_games_{GAME_NAME}_{TAG_LINE}.txt", "wb") as f:
        f.write(toon)
    print(f"Toon format export successful.")
except Exception as e:
    print(f"Warning: Could not export toon format: {e}")

print(f"Export completed for {GAME_NAME}#{TAG_LINE}. ({len(games_data)} games exported)")