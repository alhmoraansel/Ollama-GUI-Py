import os
import ctypes
import platform
import threading
import tkinter as tk
import urllib.request
import webbrowser
from bs4 import BeautifulSoup
from tkinter import ttk, font, messagebox, filedialog
from typing import Optional
import subprocess  # Import subprocess for opening file explorer
from shared_globals import *


class GUI:
    def __init__(self, root: tk.Tk, main_logic):
        self.process = None
        self.root = root
        self.main_logic = main_logic
        self.management_window: Optional[tk.Toplevel] = None
        self.download_thread = None
        self.stop_download_flag = False
        assign_global_shortcut('ctrl+d', self.toggle_dark_mode)
        assign_global_shortcut('ctrl+.', self.show_model_management_window)
        self.root.after(200, self.check_system)
        self.root.bind("<Visibility>", self.on_visibility_changed)
        self.init_layout()
        self.main_logic.refresh_models()

    def on_visibility_changed(self, event):
        if event.widget == self.root and event.state == 1:
            self.focus_input_field()

    def focus_input_field(self):
        if self.main_logic.user_input:
            self.main_logic.user_input.focus_set()

    def init_layout(self):
        self._header_frame()
        self._chat_container_frame()
        self._processbar_frame()
        self._input_frame()

    def check_system(self):
        self.apply_theme()
        if platform.system().lower() == "darwin":
            version = platform.mac_ver()[0]
            if version and 14 <= float(version) < 15:
                tcl_version = self.root.tk.call("info", "patchlevel")
                if self._version_tuple(tcl_version) <= self._version_tuple("8.6.12"):
                    messagebox.showwarning("Warning", "TK WARNING", parent=self.root)

    def _version_tuple(self, v):
        return tuple(s.zfill(8) for s in v.split("."))

    def handle_key_press(self, event: tk.Event):
        global generating_response
        if event.keysym == "Return":
            if event.state & 0x1:
                self.main_logic.user_input.insert("end", "\n")
            elif self.main_logic.send_button.cget("state") != "disabled" and not generating_response:
                self.main_logic.on_send_button(event)
            return "break"
        else:
            self.main_logic.send_button.config(state="normal")

    def resize_inner_text_widget(self, event: tk.Event):
        self.main_logic.chat_box.config(wrap=tk.WORD)

    def toggle_dark_mode(self):
        global dark_mode
        dark_mode = not dark_mode
        self.apply_theme()

    def apply_theme(self):
        style = ttk.Style()
        global dark_mode, default_font
        bg_color = "#1e1e1e" if dark_mode else "#f0f0f0"
        button_bg = "#4a4a4a" if dark_mode else "#F0F0F0"
        text_bg = "#2b2b2b" if dark_mode else "#ffffff"
        text_fg = "#ffffff" if dark_mode else "#000000"
        frame_bg = "#1e1e1e" if dark_mode else "#f0f0f0"
        selection_color = "grey" if dark_mode else "yellow" #colour of background of selected text
        selection_text = "#ffffff" if dark_mode else "purple" #colour of selected text
        user_message = "light blue" if dark_mode else "blue"
        assistant_message = "light green" if dark_mode else "green"
        other_message = "white" if dark_mode else "black"
        user_label = "pink" if dark_mode else "green"
        assistant_label = "orange" if dark_mode else "#805080"
        caret_color = "yellow" if dark_mode else "black"

        self.root.config(bg=bg_color)
        if self.management_window and self.management_window.winfo_exists():
            self.management_window.config(bg=bg_color)
            if self.main_logic.model_select:
                style_combobox(self.main_logic.model_select,default_font,text_bg,text_fg)
        if self.main_logic.chat_box and self.main_logic.user_input:
            self.main_logic.user_input.config(insertbackground =caret_color)
            self.main_logic.chat_box.config(insertbackground =caret_color)
            self.main_logic.chat_box.tag_configure("User", foreground=user_message, justify="right")
            self.main_logic.chat_box.tag_configure("Assistant", foreground=assistant_message, justify="left")
            self.main_logic.chat_box.tag_configure("user", foreground=user_message, font=(default_font, 12), justify='right')
            self.main_logic.chat_box.tag_configure("assistant", foreground=assistant_message, font=(default_font, 12), justify='left')
            self.main_logic.chat_box.tag_configure("other", foreground=other_message, font=(default_font, 12))
            self.main_logic.chat_box.tag_configure("user_label", foreground=user_label, font=(default_font, 10, "bold"), justify='right')
            self.main_logic.chat_box.tag_configure("assistant_label", foreground=assistant_label, font=(default_font, 10, "bold"), justify='left')
        for buttons in get_all_buttons(self.root):
            buttons.config(bg = button_bg, fg = text_fg)
        for frame in get_all_frames(self.root):
            if isinstance(frame, ttk.Frame):
                frame.config(style='CustomFrame.TFrame')  # Use a style for ttk.Frame
                style = ttk.Style()
                style.configure('CustomFrame.TFrame', background=frame_bg)
            elif isinstance(frame, tk.Frame):
                frame.config(bg=frame_bg) # use bg for tk.Frame
        for text_box in get_all_text_boxes(self.root):
            text_box.config(bg=text_bg,fg=text_fg,selectbackground=selection_color,selectforeground=selection_text)
        set_label_style(get_all_labels(self.root),frame_bg,text_fg)

    def create_button(self,parent, text, command, style = button_style, button_hover_bg_color = "#2980b9",width = 3):
        global dark_mode
        button = tk.Button(parent, text=text, command=command,width=width, **style)
        def on_enter(event):
            event.widget.config(bg=button_hover_bg_color)
        def on_leave(event):
            if not dark_mode:
                target_color = "#F0F0F0"
            else:
                target_color = "#4a4a4a"
            original_color = button["bg"]
            def gradual_change(step):
                if step <= 100:
                    r1, g1, b1 = button.winfo_rgb(original_color)
                    r2, g2, b2 = button.winfo_rgb(target_color)
                    r = int(r1 + (r2 - r1) * step / 100)
                    g = int(g1 + (g2 - g1) * step / 100)
                    b = int(b1 + (b2 - b1) * step / 100)
                    new_color = "#{:02x}{:02x}{:02x}".format(r >> 8, g >> 8, b >> 8)
                    button.config(bg=new_color)
                    button.after(10, lambda: gradual_change(step + 5))
            gradual_change(0)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button

    def _header_frame(self):
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(3, weight=1)
        model_select = ttk.Combobox(header_frame, state="readonly", width=30)
        model_select.grid(row=0, column=0)
        settings_button = self.create_button(header_frame, text="⚙️", command=self.show_model_management_window, width=3)
        settings_button.grid(row=0, column=1, padx=(5, 0))
        refresh_button = self.create_button(header_frame, text="Refresh", command=self.main_logic.refresh_models)
        refresh_button.grid(row=0, column=2, padx=(5, 0))
        ttk.Label(header_frame, text="Host:").grid(row=0, column=4, padx=(10, 0))
        host_input = ttk.Entry(header_frame, width=24)
        host_input.grid(row=0, column=5, padx=(5, 15))
        host_input.insert(0, self.main_logic.api_url)
        dark_mode_button = self.create_button(header_frame, text="Dark Mode", command=self.toggle_dark_mode,width=10)
        dark_mode_button.grid(row=0, column=6, padx=(5, 0))
        # Add the "Open Explorer" button
        open_explorer_button = self.create_button(header_frame, text="Explorer", command=self.open_file_explorer, width=8)
        open_explorer_button.grid(row=0, column=7, padx=(5, 0))  # Place it after Dark Mode button
        loaded_model_label = ttk.Label(header_frame, text="No Model Loaded", font=(default_font, 12))
        loaded_model_label.grid(row=0, column=3, padx=(10, 0))
        self.main_logic.model_select = model_select
        self.main_logic.refresh_button = refresh_button
        self.main_logic.host_input = host_input
        self.main_logic.loaded_model_label = loaded_model_label

    def _chat_container_frame(self):
        chat_frame = ttk.Frame(self.root)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_box = tk.Text(chat_frame, wrap=tk.WORD, state=tk.NORMAL, font=(default_font, 12), spacing1=5,highlightthickness=0,relief="flat")
        chat_box.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=chat_box.yview, style="Vertical.TScrollbar")
        scrollbar.grid(row=0, column=1, sticky="ns")
        chat_box.configure(yscrollcommand=scrollbar.set)
        #CHATBOX
        chat_box_menu = tk.Menu(chat_box, tearoff=0)
        chat_box_menu.add_command(label="Copy",command=lambda: self.main_logic.copy_text(chat_box.get("sel.first", "sel.last")))
        chat_box_menu.add_command(label="Paste", command=lambda: chat_box.insert(tk.INSERT, self.root.clipboard_get()))
        chat_box.bind("<Configure>", self.resize_inner_text_widget)
        right_click = "<Button-2>" if platform.system().lower() == "darwin" else "<Button-3>"
        chat_box.bind(right_click, lambda e: chat_box_menu.post(e.x_root, e.y_root))
        chat_box.tag_configure("Bold", foreground="#ff007b", font=(default_font, 10, "bold"))
        chat_box.tag_configure("Error", foreground="red")
        chat_box.tag_configure("other_label", foreground="red", font=(default_font, 10, "bold"))
        chat_box.bind("<<Modified>>", self.main_logic.on_chat_box_modified)
        self.main_logic.chat_box = chat_box
        self.scrollbar = scrollbar

    def _processbar_frame(self):
        process_frame = ttk.Frame(self.root, height=18)
        process_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        progress = ttk.Progressbar(process_frame, mode="indeterminate", style="TProgressbar", length=400)
        stop_button = self.create_button(process_frame, text="Stop", command=self.main_logic.on_stop_button)
        self.main_logic.progress = progress
        self.main_logic.stop_button = stop_button

    def _input_frame(self):
        input_frame = ttk.Frame(self.root)
        input_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        input_frame.grid_columnconfigure(0, weight=1)
        input_button_frame = ttk.Frame(input_frame)
        input_button_frame.grid(row=0, column=0, sticky="ew")
        input_button_frame.grid_columnconfigure(0, weight=1)
        user_input = tk.Text(input_button_frame, font=(default_font, 12), height=8, wrap=tk.WORD, relief="flat")
        user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        user_input.bind("<Key>", self.handle_key_press)
        # Add right-click menu to the input field
        user_input_menu = tk.Menu(user_input, tearoff=0)
        user_input_menu.add_command(label="Copy",command=lambda: self.main_logic.copy_text(user_input.get("sel.first", "sel.last")))
        user_input_menu.add_command(label="Paste", command=lambda: user_input.insert(tk.INSERT, self.root.clipboard_get()))
        user_input.bind("<Button-3>", lambda e: user_input_menu.post(e.x_root, e.y_root))
        send_button = self.create_button(input_button_frame, text="Send", command=self.main_logic.on_send_button)
        send_button.grid(row=0, column=1)
        send_button.config(state="disabled")
        action_button_frame = ttk.Frame(input_frame)
        action_button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        action_button_frame.grid_columnconfigure(0, weight=1)
        export_pdf_button = self.create_button(action_button_frame, text="Export to PDF",command=self.main_logic.export_chat_to_pdf, width=15)
        save_history_button = self.create_button(action_button_frame, text="Save History",command=self.main_logic.save_chat_history, width=15)
        load_history_button = self.create_button(action_button_frame, text="Load History",command=self.main_logic.restore_chat_history, width=15)
        clear_chat_button = self.create_button(action_button_frame, text="Clear Chat", command=self.confirm_clear_chat,width=15)
        stop_button = self.create_button(action_button_frame, text="Stop", command=self.main_logic.on_stop_button,width=15)
        open_chats_dir_button = self.create_button(action_button_frame, text="Open _chats Dir",command=self.open_chats_directory, width=15)
        export_pdf_button.grid(row=0, column=0, sticky="w")
        save_history_button.grid(row=0, column=1, padx=(10, 0))
        load_history_button.grid(row=0, column=2, padx=(10, 0))
        clear_chat_button.grid(row=0, column=3, padx=(10, 0))
        stop_button.grid(row=0, column=4, padx=(10, 0))
        open_chats_dir_button.grid(row=0, column=5, padx=(10, 0))
        self.main_logic.user_input = user_input
        self.main_logic.send_button = send_button
        self.root.after(100, self.focus_input_field)
        threading.Timer(0.5, self.main_logic.refresh_models).start()

    def show_model_management_window(self):
        def _download_confirmed(model_name):
            download_button.config(state="disabled")
            stop_download_button.config(state="normal")
            model_name_input.config(state="disabled")
            self.stop_download_flag = False
            self.download_thread = threading.Thread(target=self.main_logic.download_model, args=(model_name,))
            self.download_thread.start()

        def _download():
            model_name = model_name_input.get().strip()
            if not model_name:
                messagebox.showerror("Error", "Please enter a model name.", parent=management_window)
                return
            try:
                model_size = self.get_model_size_from_ollama_website(model_name)
                if model_size is None:
                    messagebox.showwarning("Warning", f"Could not determine the size of model '{model_name}'.",parent=management_window)
                    return
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}", parent=management_window)
                return
            confirm = messagebox.askyesno("Confirm Download",f"Are you sure you want to download model '{model_name}'? (Size: {model_size:.2f} MB)",parent=management_window,)
            if confirm:
                _download_confirmed(model_name)

        def _delete():
            model_name = self.main_logic.models_list.get(tk.ACTIVE).strip()
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete model '{model_name}'?",
                parent=management_window,
            )
            if confirm:
                self.main_logic.delete_model(model_name)

        def unload_models():
            self.main_logic.free_memory()

        management_window = tk.Toplevel(self.root)
        management_window.title("Model Management")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (600 / 2))
        y = int((screen_height / 2) - (500 / 2))
        management_window.geometry(f"{600}x{500}+{x}+{y}")
        management_window.grid_columnconfigure(0, weight=1)
        management_window.grid_rowconfigure(3, weight=1)
        frame = ttk.Frame(management_window)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        model_name_input = ttk.Entry(frame)
        model_name_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        model_name_input.bind("<Return>", lambda event: _download())  # added this line
        download_button = self.create_button(frame, text="Download", command=_download)
        download_button.grid(row=0, column=1, sticky="ew")
        stop_download_button = self.create_button(frame, text="Stop Download", command=self.stop_download,width=10)
        stop_download_button.grid(row=1, column=1, sticky="ew")
        stop_download_button.config(state="disabled")
        tips = tk.Label(frame, text="find models: https://ollama.com/library", fg="blue", cursor="hand2")
        tips.bind("<Button-1>", lambda e: webbrowser.open("https://ollama.com/library"))
        tips.grid(row=1, column=0, sticky="W", padx=(0, 5), pady=5)
        list_action_frame = ttk.Frame(management_window)
        list_action_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        list_action_frame.grid_columnconfigure(0, weight=1)
        list_action_frame.grid_rowconfigure(0, weight=1)
        models_list = tk.Listbox(list_action_frame)
        models_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_action_frame, orient="vertical", command=models_list.yview,style="Vertical.TScrollbar")
        scrollbar.grid(row=0, column=1, sticky="ns")
        models_list.config(yscrollcommand=scrollbar.set)
        delete_button = self.create_button(list_action_frame, text="Delete", command=_delete)
        delete_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        stop_ollama_button = self.create_button(list_action_frame, text="Free Memory", command=unload_models,width=10)
        stop_ollama_button.grid(row=0, column=3, sticky="ew", padx=(5, 0))
        log_textbox = tk.Text(management_window)
        log_textbox.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        log_textbox.config(state="disabled")
        progress_label = ttk.Label(management_window, text="")
        progress_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)
        self.management_window = management_window
        self.main_logic.log_textbox = log_textbox
        self.main_logic.download_button = download_button
        self.main_logic.delete_button = delete_button
        self.main_logic.models_list = models_list
        self.main_logic.update_model_list()
        self.apply_theme()
        self.progress_label = progress_label
        model_name_input.focus_set()

    def update_progress_label(self, text):
        self.progress_label.config(text=text)

    def confirm_clear_chat(self):
        if messagebox.askokcancel("Clear Chat","Are you sure you want to clear the chat history?",parent=self.root):self.main_logic.clear_chat()

    def get_model_size_from_ollama_website(self, model_name):
        try:
            url = f"https://ollama.com/library/{model_name}"
            with urllib.request.urlopen(url) as response:
                html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            tags_nav = soup.find('nav', {'id': 'tags-nav'})
            if tags_nav:
                size_span = tags_nav.find('span', class_='text-xs text-neutral-400')
                if size_span:
                    size_text = size_span.text.strip()
                    if "GB" in size_text:
                        return float(size_text.replace("GB", "").strip()) * 1024
                    elif "MB" in size_text:
                        return float(size_text.replace("MB", "").strip())
            return None
        except Exception as e:
            print(f"Error fetching model size: {e}")
            return None

    def stop_download(self):
        if hasattr(self, 'download_thread') and self.download_thread.is_alive():
            thread_id = self.get_id(self.download_thread)
            self.raise_exception(thread_id)
            self.download_thread.join(timeout=0.1)
            if self.download_thread.is_alive():
                print("Thread did not terminate gracefully")
        if self.management_window and self.management_window.winfo_exists():
            self.management_window.destroy()
        if hasattr(self, 'downloaded_file_path'):
            try:
                os.remove(self.downloaded_file_path)
                print(f"Deleted file: {self.downloaded_file_path}")
            except Exception as e:
                print(f"Error deleting file: {e}")
        else:
            print("No download to stop.")

    def raise_exception(self, thread_id):
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def get_id(self, thread):
        for id, t in threading._active.items():
            if t is thread:
                return id
        return None

    def open_file_explorer(self):
        """Opens the file explorer in the current working directory."""
        cwd = os.getcwd()
        if platform.system() == "Windows":
            os.startfile(cwd)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", cwd])
        else:  # Linux
            subprocess.Popen(["xdg-open", cwd])

    def open_chats_directory(self):
        """Opens the file explorer in the _chats directory."""
        chats_dir = os.path.join(os.getcwd(), "_chats")
        # Create the directory if it doesn't exist
        if not os.path.exists(chats_dir):
            os.makedirs(chats_dir)
        if platform.system() == "Windows":
            os.startfile(chats_dir)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", chats_dir])
        else:  # Linux
            subprocess.Popen(["xdg-open", chats_dir])
