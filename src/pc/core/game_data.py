"""Game data: words and clues for each round loaded from YAML."""

import os
import yaml

from .models import Clue, InformationType, PlayerSection, Round


def _load_rounds_config() -> dict:
    """Load rounds configuration from YAML file.

    Returns:
        Dictionary with rounds configuration
    """
    config_path = os.path.join(os.path.dirname(__file__), "rounds.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Error loading rounds.yaml: {e}")
        return {"rounds": []}


def create_game_rounds() -> list[Round]:
    """Create all game rounds with words and clues from YAML configuration.

    Returns:
        List of Round objects
    """
    config = _load_rounds_config()
    rounds = []

    for round_data in config.get("rounds", []):
        round_number = round_data["round_number"]
        word = round_data["word"]
        clue_type_str = round_data["clue_type"]
        clue_type = InformationType[clue_type_str.upper()]

        round_obj = Round(
            round_number=round_number,
            word=word,
            clue_type=clue_type
        )

        # Create player sections with clues
        player_sections = []
        for clue_data in round_data.get("clues", []):
            player_id = clue_data["player"]
            content = clue_data["content"]

            player_section = PlayerSection(
                player_id=player_id,
                clue=Clue(clue_type, content)
            )
            player_sections.append(player_section)

        round_obj.player_sections = player_sections
        rounds.append(round_obj)

    return rounds
