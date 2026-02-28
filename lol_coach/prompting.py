import json
import os


def read_prompt_template(prompt_path: str) -> str:
    """Load and return the prompt template from disk."""
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(games_data: list[dict], prompt_path: str) -> str:
    """Inject serialized games_data into the prompt template."""
    template = read_prompt_template(prompt_path)
    data_text = json.dumps(games_data, ensure_ascii=True)
    marker = "[DATA]"
    if marker in template:
        return template.replace(marker, data_text)
    return f"{template}\n\n{data_text}"
