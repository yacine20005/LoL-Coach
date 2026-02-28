"""lol_coach — Riot Games API utilities and match data processing."""

from .export_service import collect_games_data, export_tabular_files, export_toon_file
from .match_processing import build_game_record, find_player_participant
from .prompting import build_prompt
from .riot_api import build_headers, fetch_match_info, get_match_ids, get_puuid
from .text_utils import chunk_text

__all__ = [
    "build_headers",
    "get_puuid",
    "get_match_ids",
    "fetch_match_info",
    "find_player_participant",
    "build_game_record",
    "collect_games_data",
    "export_tabular_files",
    "export_toon_file",
    "build_prompt",
    "chunk_text",
]
