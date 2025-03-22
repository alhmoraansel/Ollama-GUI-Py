import keyboard
import re
import json

chat_history = []
generating_response = None
dark_mode = False
default_font = "Congenial"
button_font = ("Congenial", 12)
button_style = {
    "font": button_font,
    "relief": "flat",
    "bd": 0,
    "highlightthickness": 0,
    "padx": 20,
    "pady": 10,
    "cursor": "hand2",
    "borderwidth": 0,
    "highlightbackground": "#e8eaed",
    "highlightcolor": "#e8eaed",
}
message_index = 0
parse_required = False
loading_message_from_json = False

def filter_by_role(history, role):
    return [m for m in history if m['role'] == role] if isinstance(history, list) and isinstance(role, str) else []

def convert_input_to_chat_history(text):
    """
    Converts a text input into a structured chat history format.

    Parses a text where user and assistant messages are delineated,
    extracting the role, content, and order of each message. Handles
    multi-line assistant responses and assigns a model tag.

    Args:
        text (str): The input text containing the chat history.
            User messages should start with "You:".
            Assistant messages should start with "{model_tag}:".

    Returns:
        list: A list of dictionaries, where each dictionary represents a message
              with the following keys:
                - "role" (str): "user" or "assistant".
                - "content" (str): The message text.
                - "index" (int): The order of the message in the chat.
                - "model" (str, optional): The model tag for assistant
                  messages.
    """
    history = []
    index = 0
    text = re.sub(r'\n{2,}', '\n', text)
    lines = text.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == "You:":
            # Check if the next line is the content of the user message
            if i + 1 < len(lines):
                content = lines[i + 1].strip()
                history.append({"role": "user", "content": content, "index": index})
                i += 2  # Skip the "You:" line and the content line
            else:
                print(f"Skipping invalid message format: {line}")
                i += 1
        elif ":" in line:
            parts = line.split(":", 1)
            model_tag = parts[0].strip()
            content_lines = [parts[1].strip()]
            i += 1
            while i < len(lines) and not lines[i].startswith("You:"):
                content_lines.append(lines[i].strip())
                i += 1
            content = "\n".join(content_lines).strip()
            # Remove "latest\n" if it exists at the start of the content
            if content.startswith("latest\n"):
                content = content[len("latest\n"):].strip()
            history.append({"role": "assistant", "content": content, "index": index, "model": model_tag})
            index += 1
        else:
            print(f"Skipping invalid message format: {line}")
            i += 1
    return history

def assign_global_shortcut(key, callback):
    keyboard.add_hotkey(key, callback)

def restore_chat_history_from_json(file_path):
    global loading_message_from_json
    loading_message_from_json = True
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception:
        return None

def get_items_by_key_value(data, target_key, target_value, result_key=None):
    results = []

    def _search(obj):
        if isinstance(obj, dict):
            if target_key in obj and obj[target_key] == target_value:
                results.append(obj[result_key] if result_key and result_key in obj else obj)
            for val in obj.values():
                _search(val)
        elif isinstance(obj, list):
            for item in obj:
                _search(item)
    _search(data)
    return results

def sort_items_ascending(items, sort_by):
    return sorted(items, key=lambda item: item[sort_by] if isinstance(item, dict) else item) if items and sort_by else items
