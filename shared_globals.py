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
    "fg":"white",
    "relief": "flat",
    "padx": 20,
    "pady": 10,
    "cursor": "hand2",
    "bd" :0,
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



#GUI RELATED STUFF
import tkinter as tk
from tkinter import ttk

def get_all_buttons(root):
    """
    Recursively retrieves all Button and ttk.Button widgets within a Tkinter root window.

    Args:
        root: The Tkinter root window or any container widget.

    Returns:
        list: A list of all Button and ttk.Button widgets found.
    """
    buttons = []
    widgets = root.winfo_children()  #gets all the child widgets.
    for widget in widgets:
        if isinstance(widget, tk.Button) or isinstance(widget, ttk.Button):
            buttons.append(widget)
        else:
            buttons.extend(get_all_buttons(widget))  # Recurse into child containers.
    return buttons


def get_all_frames(root):
    """
    Recursively retrieves all Frame and ttk.Frame widgets.

    Args:
        root: The Tkinter root window or any container widget.

    Returns:
        list: A list of all Frame and ttk.Frame widgets found.
    """
    frames = []
    widgets = root.winfo_children()

    for widget in widgets:
        if isinstance(widget, tk.Frame) or isinstance(widget, ttk.Frame):
            frames.append(widget)
            frames.extend(get_all_frames(widget))  # Recurse into child frames.
        else:
            frames.extend(get_all_frames(widget))
    return frames


def get_all_text_boxes(root):
    """
    Recursively retrieves all Text widgets.

    Args:
        root: The Tkinter root window or any container widget.

    Returns:
        list: A list of all Text widgets found.
    """
    text_boxes = []
    widgets = root.winfo_children()

    for widget in widgets:
        if isinstance(widget, tk.Text):
            text_boxes.append(widget)
        else:
            text_boxes.extend(get_all_text_boxes(widget))
    return text_boxes


def get_all_entries(root):
    """Recursively retrieves all Entry widgets.

    Args:
        root: The Tkinter root or container widget.

    Returns:
        list: A list of all Entry widgets.
    """
    entries = []
    widgets = root.winfo_children()
    for widget in widgets:
        if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Entry):
            entries.append(widget)
        else:
            entries.extend(get_all_entries(widget))
    return entries

def set_entry_style(entry_list, bg_color, fg_color):
    """Sets the background and foreground colors for a list of Entry widgets.

    Args:
        entry_list: A list of Tkinter Entry or ttk.Entry widgets.
        bg_color: The background color to set.
        fg_color: The foreground color to set.
    """
    for entry in entry_list:
        if isinstance(entry, ttk.Entry):
            style = ttk.Style()
            style.configure("CustomEntry.TEntry", background=bg_color, foreground=fg_color, fieldbackground=bg_color)  # Added fieldbackground
            entry.config(style="CustomEntry.TEntry")
        else:
            entry.config(bg=bg_color, fg=fg_color)


def get_all_labels(root):
    """Recursively retrieves all Label widgets.

    Args:
        root: The Tkinter root or container widget.

    Returns:
        list: A list of all Label widgets.
    """
    labels = []
    widgets = root.winfo_children()
    for widget in widgets:
        if isinstance(widget, tk.Label) or isinstance(widget, ttk.Label):
            labels.append(widget)
        else:
            labels.extend(get_all_labels(widget))
    return labels

def set_label_style(label_list, bg_color, fg_color):
    """Sets the background and foreground colors for a list of Label widgets.

    Args:
        label_list: A list of Tkinter Label or ttk.Label widgets.
        bg_color: The background color to set.
        fg_color: The foreground color to set.
    """
    for label in label_list:
        if isinstance(label, ttk.Label):
            style = ttk.Style()
            style.configure("CustomLabel.TLabel", background=bg_color, foreground=fg_color)
            label.config(style="CustomLabel.TLabel")
        else:
            label.config(bg=bg_color, fg=fg_color)



def style_combobox(combobox, font, bg_color, fg_color):
    """
    Styles a Combobox widget.

    Args:
        combobox: The Combobox widget to style.
        font:  The font to apply.
        bg_color: The background color.
        fg_color: The foreground color.
    """
    style = ttk.Style()
    style.configure("Custom.TCombobox",
                    background=bg_color,
                    foreground=fg_color,
                    font=font,
                    fieldbackground=bg_color,
                    )
    combobox.config(style="Custom.TCombobox")
    combobox.option_add('*TCombobox.Listbox.background', bg_color)
    combobox.option_add('*TCombobox.Listbox.foreground', fg_color)