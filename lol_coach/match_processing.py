def find_player_participant(info: dict, puuid: str) -> dict | None:
    """Return the participant entry matching the given PUUID, or None."""
    for participant in info.get("participants", []):
        if participant.get("puuid") == puuid:
            return participant
    return None


def compute_core_metrics(participant: dict, duration: int) -> dict:
    """Compute KDA, total CS, and CS per minute from participant data."""
    kills, assists, deaths = participant["kills"], participant["assists"], participant["deaths"]
    kda = (kills + assists) / max(1, deaths)

    cs = participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]
    cs_per_min = cs / (duration / 60)

    return {
        "kda": round(kda, 2),
        "cs": cs,
        "cs_per_min": round(cs_per_min, 2),
    }


def extract_items(participant: dict) -> list[int]:
    """Return the seven item slot IDs for the participant."""
    return [participant.get(f"item{i}", 0) for i in range(7)]


def _position_fields(participant: dict) -> dict:
    return {
        "champion": participant["championName"],
        "role": participant["role"],
        "lane": participant["lane"],
        "team_position": participant.get("teamPosition", ""),
        "individual_position": participant.get("individualPosition", ""),
    }


def _combat_fields(participant: dict, metrics: dict) -> dict:
    return {
        "win": participant["win"],
        "kills": participant["kills"],
        "deaths": participant["deaths"],
        "assists": participant["assists"],
        "kda": metrics["kda"],
        "cs": metrics["cs"],
        "cs_per_min": metrics["cs_per_min"],
        "champ_level": participant.get("champLevel", 0),
        "champ_experience": participant.get("champExperience", 0),
        "killing_sprees": participant.get("killingSprees", 0),
        "largest_killing_spree": participant.get("largestKillingSpree", 0),
        "pentakills": participant.get("pentaKills", 0),
        "quadrakills": participant.get("quadraKills", 0),
        "triplekills": participant.get("tripleKills", 0),
        "doublekills": participant.get("doubleKills", 0),
        "multikills": participant.get("largestMultiKill", 0),
        "first_blood_kill": participant.get("firstBloodKill", False),
        "first_blood_assist": participant.get("firstBloodAssist", False),
        "largest_critical_strike": participant.get("largestCriticalStrike", 0),
    }


def _damage_fields(participant: dict) -> dict:
    return {
        "damage_dealt": participant["totalDamageDealtToChampions"],
        "physical_damage_to_champs": participant.get("physicalDamageDealtToChampions", 0),
        "magic_damage_to_champs": participant.get("magicDamageDealtToChampions", 0),
        "true_damage_to_champs": participant.get("trueDamageDealtToChampions", 0),
        "physical_damage_dealt": participant.get("physicalDamageDealt", 0),
        "magic_damage_dealt": participant.get("magicDamageDealt", 0),
        "true_damage_dealt": participant.get("trueDamageDealt", 0),
        "damage_taken": participant["totalDamageTaken"],
        "physical_damage_taken": participant.get("physicalDamageTaken", 0),
        "magic_damage_taken": participant.get("magicDamageTaken", 0),
        "true_damage_taken": participant.get("trueDamageTaken", 0),
        "damage_self_mitigated": participant.get("damageSelfMitigated", 0),
        "true_mitigated_damage": participant.get("damageSelfMitigated", 0),
        "total_heal": participant["totalHeal"],
        "total_heal_on_teammates": participant.get("totalHealsOnTeammates", 0),
        "damage_shielded_on_teammates": participant.get("totalDamageShieldedOnTeammates", 0),
        "total_cc_dealt": participant.get("timeCCingOthers", 0),
        "total_time_cc_dealt": participant.get("totalTimeCCDealt", 0),
    }


def _economy_fields(participant: dict, items: list[int]) -> dict:
    return {
        "gold": participant["goldEarned"],
        "gold_spent": participant.get("goldSpent", 0),
        "item0": items[0],
        "item1": items[1],
        "item2": items[2],
        "item3": items[3],
        "item4": items[4],
        "item5": items[5],
        "item6": items[6],
        "items_purchased": participant.get("itemsPurchased", 0),
        "consumables_purchased": participant.get("consumablesPurchased", 0),
        "summoner1_id": participant.get("summoner1Id", 0),
        "summoner2_id": participant.get("summoner2Id", 0),
        "summoner1_casts": participant.get("summoner1Casts", 0),
        "summoner2_casts": participant.get("summoner2Casts", 0),
        "spell1_casts": participant.get("spell1Casts", 0),
        "spell2_casts": participant.get("spell2Casts", 0),
        "spell3_casts": participant.get("spell3Casts", 0),
        "spell4_casts": participant.get("spell4Casts", 0),
    }


def _vision_fields(participant: dict) -> dict:
    return {
        "vision_score": participant["visionScore"],
        "wards_placed": participant["wardsPlaced"],
        "wards_killed": participant.get("wardsKilled", 0),
        "sight_wards_bought": participant.get("sightWardsBoughtInGame", 0),
        "vision_wards_bought": participant.get("visionWardsBoughtInGame", 0),
        "detector_wards_placed": participant.get("detectorWardsPlaced", 0),
    }


def _objective_fields(participant: dict) -> dict:
    return {
        "damage_dealt_to_objectives": participant.get("damageDealtToObjectives", 0),
        "damage_dealt_to_buildings": participant.get("damageDealtToBuildings", 0),
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
        "first_tower_kill": participant.get("firstTowerKill", False),
        "first_tower_assist": participant.get("firstTowerAssist", False),
    }


def _challenge_fields(challenges: dict) -> dict:
    return {
        "gold_per_minute": round(challenges.get("goldPerMinute", 0), 2),
        "damage_per_minute": round(challenges.get("damagePerMinute", 0), 2),
        "vision_score_per_minute": round(challenges.get("visionScorePerMinute", 0), 2),
        "kill_participation": round(challenges.get("killParticipation", 0), 3),
        "kda_challenge": round(challenges.get("kda", 0), 2),
        "damage_taken_on_team_percentage": round(challenges.get("damageTakenOnTeamPercentage", 0), 3),
        "max_level_lead_lane_opponent": challenges.get("maxLevelLeadLaneOpponent", 0),
        "max_cs_advantage_on_lane_opponent": round(challenges.get("maxCsAdvantageOnLaneOpponent", 0), 2),
        "takedowns": challenges.get("takedowns", 0),
        "takedowns_first_25_minutes": challenges.get("takedownsFirst25Minutes", 0),
        "deaths_by_enemy_champs": challenges.get("deathsByEnemyChamps", 0),
        "enemy_champ_immobilizations": challenges.get("enemyChampionImmobilizations", 0),
        "solo_kills": challenges.get("soloKills", 0),
        "outnumbered_kills": challenges.get("outnumberedKills", 0),
    }


def _game_state_fields(participant: dict, duration: int) -> dict:
    return {
        "time_played": participant.get("timePlayed", 0),
        "longest_time_alive": participant.get("longestTimeSpentLiving", 0),
        "total_time_dead": participant.get("totalTimeSpentDead", 0),
        "bounce_level": participant.get("bountyLevel", 0),
        "unrealized_kills": participant.get("unrealKills", 0),
        "game_ended_in_surrender": participant.get("gameEndedInSurrender", False),
        "game_ended_in_early_surrender": participant.get("gameEndedInEarlySurrender", False),
        "team_early_surrendered": participant.get("teamEarlySurrendered", False),
        "game_duration": duration,
    }


def build_game_record(participant: dict, duration: int) -> dict:
    """Assemble a flat stats record for a single game from participant data."""
    metrics = compute_core_metrics(participant, duration)
    items = extract_items(participant)
    challenges = participant.get("challenges", {})

    return {
        **_position_fields(participant),
        **_combat_fields(participant, metrics),
        **_damage_fields(participant),
        **_economy_fields(participant, items),
        **_vision_fields(participant),
        **_objective_fields(participant),
        **_challenge_fields(challenges),
        **_game_state_fields(participant, duration),
    }
