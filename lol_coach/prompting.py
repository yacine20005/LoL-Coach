import json
import os


def read_prompt_template(prompt_path):
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(games_data, prompt_path):
    template = read_prompt_template(prompt_path)
    data_text = json.dumps(games_data, ensure_ascii=True)
    marker = "[COPIER LES DONNEES CSV/JSON ICI]"
    if marker in template:
        return template.replace(marker, data_text)
    return f"{template}\n\n{data_text}"
