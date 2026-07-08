"""Game data: words and clues for each round loaded from YAML."""

from __future__ import annotations

import os
import yaml
import random
from typing import Any, Dict, List

from .models import Clue, InformationType, PlayerSection, Round


def _load_rounds_config() -> Dict[str, Any]:
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
        return {}


def create_game_rounds() -> List[Round]:
    """Create all game rounds with words and clues from YAML configuration.

    Returns:
        List of Round objects
    """
    config = _load_rounds_config()
    rounds = []
    selected_rounds = [
        ("single_word_rounds", random.choice(config["single_word_rounds"])),
        ("phrase_rounds", random.choice(config["phrase_rounds"])),
        ("image_rounds", random.choice(config["image_rounds"])),
        ("audio_rounds", random.choice(config["audio_rounds"])),
        ("mixed_rounds", random.choice(config["mixed_rounds"])),
    ]

    for round_number, (category_name, round_data) in enumerate(selected_rounds, start=1):
        clue_types = {clue_data["type"].upper() for clue_data in round_data["clues"]}
        if category_name == "mixed_rounds" or len(clue_types) > 1:
            clue_type = InformationType.MIXED
        else:
            clue_type = InformationType[next(iter(clue_types))]

        round_obj = Round(
            round_number=round_number,
            word=round_data["word"],
            clue_type=clue_type,
        )

        # Create player sections with clues
        player_sections = []
        for clue_data in round_data["clues"]:
            player_id = clue_data["player"]
            clue_type = InformationType[clue_data["type"].upper()]
            content = clue_data["content"]

            player_section = PlayerSection(
                player_id=player_id,
                clue=Clue(clue_type, content)
            )
            player_sections.append(player_section)

        round_obj.player_sections = player_sections
        rounds.append(round_obj)

    return rounds
