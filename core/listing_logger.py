from datetime import datetime
import os
import json 
from typing import Dict, Any

script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, '..', 'logs', 'listings.txt')

SCRIPT_PARAMS_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'web', 'webui', 'script_params.json')
)

def get_params() -> Dict[str, Any]:
    if os.path.exists(SCRIPT_PARAMS_FILE):
        with open(SCRIPT_PARAMS_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}


def write_to_file(content: str, filename=log_file_path, max_lines=20):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f'{timestamp} - {content}\n'

    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, '..', '..', filename)

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    lines.insert(0, log_line)
    lines = lines[:max_lines]

    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(lines)
