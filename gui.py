import os
import ctypes, platform, threading, tkinter as tk, urllib.request, webbrowser
from bs4 import BeautifulSoup
from tkinter import ttk, font, messagebox, filedialog
from typing import Optional
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
        fg_color = "#ffffff" if dark_mode else "#000000"
        button_bg = "#333333" if dark_mode else "#e0e0e0"
        button_fg = "#ffffff" if dark_mode else "#000000"
        text_bg = "#2b2b2b" if dark_mode else "#ffffff"
        text_fg = "#ffffff" if dark_mode else "#000000"
        progressbar_trough = "#333333" if dark_mode else "#e0e0e0"
        progressbar_bar = "#4d94ff"
        frame_bg = "#1e1e1e" if dark_mode else "#f0f0f0"
        entry_bg = "#444444" if dark_mode else "#ffffff"
        entry_fg = "#ffffff" if dark_mode else "#000000"
        self.root.config(bg=bg_color)
        self.main_logic.chat_box.config(bg=text_bg, fg=text_fg, font=(default_font, 12), selectbackground="yellow")
        self.main_logic.model_select.config(foreground=fg_color, background=button_bg, font=(default_font, 12))
        self.main_logic.host_input.config(foreground=fg_color, background=entry_bg, font=(default_font, 12))
        style.configure("TButton", background=button_bg, foreground=fg_color, font=(default_font, 12))
        style.map("TButton", background=[("active", "#555555" if dark_mode else "#c0c0c0")])
        for attr_name in dir(self.main_logic):
            attr = getattr(self.main_logic, attr_name)
            if isinstance(attr, ttk.Button):
                attr.config(style="TButton")
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.config(style="TFrame")
        style.configure("TFrame", background=frame_bg)
        if self.management_window and self.management_window.winfo_exists():
            self.management_window.config(bg=bg_color)
            for widget in self.management_window.winfo_children():
                if isinstance(widget, ttk.Frame):
                    widget.config(style="TFrame")
                elif isinstance(widget, ttk.Button):
                    widget.config(style="TButton")
                elif isinstance(widget, tk.Listbox):
                    widget.config(bg=text_bg, fg=text_fg, font=(default_font, 12))
                elif isinstance(widget, tk.Text):
                    widget.config(bg=text_bg, fg=text_fg, font=(default_font, 12), insertbackground=text_fg)
                elif isinstance(widget, ttk.Entry):
                    widget.config(foreground=fg_color, background=entry_bg, font=(default_font, 12))

    def create_button(self, parent, text, command, style=None, button_hover_bg_color="#2980b9", width=10):
        style = style or button_style
        button = tk.Button(parent, text=text, command=command, width=width, **style)
        initial_bg = style.get("background", button["background"])
        button.bind("<Enter>", lambda e: e.widget.config(bg=button_hover_bg_color))
        button.bind("<Leave>", lambda e: e.widget.config(bg=initial_bg))
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
        dark_mode_button = self.create_button(header_frame, text="Dark Mode", command=self.toggle_dark_mode)
        dark_mode_button.grid(row=0, column=6, padx=(5, 0))
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
        chat_box = tk.Text(chat_frame, wrap=tk.WORD, state=tk.NORMAL, font=(default_font, 12), spacing1=5, highlightthickness=0, selectbackground="yellow", relief="flat")
        chat_box.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=chat_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        chat_box.configure(yscrollcommand=scrollbar.set)
        chat_box_menu = tk.Menu(chat_box, tearoff=0)
        chat_box_menu.add_command(label="Copy", command=lambda: self.main_logic.copy_text(chat_box.get("sel.first", "sel.last")))
        chat_box_menu.add_command(label="Paste", command=lambda: chat_box.insert(tk.INSERT, self.root.clipboard_get()))
        chat_box.bind("<Configure>", self.resize_inner_text_widget)
        right_click = "<Button-2>" if platform.system().lower() == "darwin" else "<Button-3>"
        chat_box.bind(right_click, lambda e: chat_box_menu.post(e.x_root, e.y_root))
        chat_box.tag_configure("user", foreground="#003366", font=(default_font, 12), justify='right')
        chat_box.tag_configure("assistant", foreground="#006400", font=(default_font, 12), justify='left')
        chat_box.tag_configure("other", foreground="#444444", font=(default_font, 12))
        chat_box.tag_configure("user_label", foreground="red", font=(default_font, 10, "bold"), justify='right')
        chat_box.tag_configure("assistant_label", foreground="red", font=(default_font, 10, "bold"), justify='left')
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
        user_input = tk.Text(input_button_frame, font=(default_font, 12), height=8, wrap=tk.WORD, relief="flat", selectbackground="purple")
        user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        user_input.bind("<Key>", self.handle_key_press)
        send_button = self.create_button(input_button_frame, text="Send", command=self.main_logic.on_send_button)
        send_button.grid(row=0, column=1)
        send_button.config(state="disabled")
        action_button_frame = ttk.Frame(input_frame)
        action_button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        action_button_frame.grid_columnconfigure(0, weight=1)
        export_pdf_button = self.create_button(action_button_frame, text="Export to PDF", command=self.main_logic.export_chat_to_pdf, width=15)
        save_history_button = self.create_button(action_button_frame, text="Save History", command=self.main_logic.save_chat_history, width=15)
        load_history_button = self.create_button(action_button_frame, text="Load History", command=self.main_logic.restore_chat_history, width=15)
        clear_chat_button = self.create_button(action_button_frame, text="Clear Chat", command=self.confirm_clear_chat, width=15)
        stop_button = self.create_button(action_button_frame, text="Stop", command=self.main_logic.on_stop_button, width=15)
        export_pdf_button.grid(row=0, column=0, sticky="w")
        save_history_button.grid(row=0, column=1, padx=(10, 0))
        load_history_button.grid(row=0, column=2, padx=(10, 0))
        clear_chat_button.grid(row=0, column=3, padx=(10, 0))
        stop_button.grid(row=0, column=4, sticky="e")
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
                    messagebox.showwarning("Warning", f"Could not determine the size of model '{model_name}'.", parent=management_window)
                    return
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}", parent=management_window)
                return
            confirm = messagebox.askyesno(
                "Confirm Download",
                f"Are you sure you want to download model '{model_name}'? (Size: {model_size:.2f} MB)",
                parent=management_window,
            )
            if confirm:
                _download_confirmed(model_name)

        def _delete():
            self.main_logic.delete_model(self.main_logic.models_list.get(tk.ACTIVE).strip())

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
        model_name_input.bind("<Return>", lambda event: _download()) # added this line
        download_button = self.create_button(frame, text="Download", command=_download)
        download_button.grid(row=0, column=1, sticky="ew")
        stop_download_button = self.create_button(frame, text="Stop Download", command=self.stop_download)
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
        scrollbar = ttk.Scrollbar(list_action_frame, orient="vertical", command=models_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        models_list.config(yscrollcommand=scrollbar.set)
        delete_button = self.create_button(list_action_frame, text="Delete", command=_delete)
        delete_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        stop_ollama_button = self.create_button(list_action_frame, text="Free Memory", command=unload_models)
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
        if messagebox.askokcancel("Clear Chat", "Are you sure you want to clear the chat history? This action cannot be undone.", parent=self.root):
            self.main_logic.clear_chat()

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
