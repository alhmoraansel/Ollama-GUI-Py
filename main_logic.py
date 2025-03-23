import json, os, urllib.parse, urllib.request, time, tkinter as tk, subprocess, markdown
from shared_globals import *
from threading import Thread
from typing import List, Generator, Optional
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from tkinter import ttk, filedialog
from gui import *
from AppOpener import close

class OllamaInterfaceLogic:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.api_url = "http://127.0.0.1:11434"
        self.editor_window: Optional[tk.Toplevel] = None
        self.loaded_model = None
        self.message_index = message_index
        global chat_history
        self.chat_history = chat_history
        self.loading_messages = loading_message_from_json
        self.user_editing = parse_required
        self.ai_running = generating_response
        self.ai_running = False
        self.chat_box_modified_by = "user"
        assign_global_shortcut('ctrl+s', self.save_chat_history)
        assign_global_shortcut('ctrl+o', self.restore_chat_history)
        assign_global_shortcut('ctrl+shift+s', self.export_chat_to_pdf)
        assign_global_shortcut('ctrl+p', self.export_chat_to_pdf)
        os.makedirs("_chats", exist_ok=True)

    def update_host(self):
        self.api_url = self.host_input.get()

    def refresh_models(self):
        self.update_host()
        self.model_select.config(foreground="black")
        self.model_select.set("Waiting...")
        self.send_button.config(state="disabled")
        self.refresh_button.config(state="normal")
        Thread(target=self.update_model_select, daemon=True).start()

    def update_model_select(self):
        try:
            models = self.fetch_models()
            self.model_select["values"] = models
            if models:
                self.model_select.set(models[0])
            else:
                self.show_error("You need to download a model!")
        except Exception:
            self.show_error("Error! Please check the host.")
        finally:
            self.refresh_button.config(state="normal")

    def update_model_list(self):
        if self.models_list.winfo_exists():
            self.models_list.delete(0, tk.END)
            try:
                models = self.fetch_models()
                self.models_list.insert(tk.END, *models)
            except Exception:
                self.append_log_to_inner_textbox("Error! Please check the Ollama host.")

    def on_send_button(self, _=None):
        if not self.ai_running:
            message = self.user_input.get("1.0", "end-1c")
            self.update_loaded_model_label()
            if message:
                self.append_text_to_chat("You: \n", ("user_label",))
                self.append_text_to_chat(f"{message}\n\n", ("user",))
                self.user_input.delete("1.0", "end")
                self.chat_history.append({"role": "user", "content": message, "index": self.message_index})
                Thread(target=self.generate_ai_response, daemon=True).start()
                self.save_chat_history()

    def generate_ai_response(self):
        self.ai_running = True
        self.show_process_bar()
        self.send_button.config(state="disabled")
        self.refresh_button.config(state="normal")
        model_name = self.model_select.get()
        self.append_text_to_chat(f"{model_name}\n", ("assistant_label",))
        ai_message = ""
        for i in self.fetch_chat_stream_result():
            if self.stop_button.cget("state") == "disabled":
                break
            self.append_text_to_chat(f"{i}", ("Assistant",))
            ai_message += i
            self.update_loaded_model_label()
        self.chat_history.append({"role": "assistant", "content": ai_message, "index": self.message_index, "model": model_name})
        self.message_index += 1
        self.append_text_to_chat("\n\n", ("Assistant",))
        self.hide_process_bar()
        self.send_button.config(state="normal")
        self.refresh_button.config(state="normal")
        self.stop_button.config(state="normal")
        self.save_chat_history()
        self.chat_box.config(state=tk.NORMAL)
        self.ai_running = False

    def on_stop_button(self):
        self.stop_button.config(state="disabled")
        self.refresh_button.config(state="normal")
        self.hide_process_bar()
        self.ai_running = False
        self.chat_box.config(state=tk.NORMAL)

    def fetch_models(self) -> List[str]:
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            lines = result.stdout.strip().split('\n')
            models = [line.split()[0] for line in lines[1:] if line]
            return models
        except Exception as e:
            self.show_error(f"Error fetching models: {e}")
            return []

    def fetch_chat_stream_result(self) -> Generator:
        request = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/chat"),
            data=json.dumps({"model": self.model_select.get(), "messages": self.chat_history, "stream": True}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request) as resp:
            for line in resp:
                if self.stop_button.cget("state") == "disabled":
                    break
                data = json.loads(line.decode("utf-8"))
                if "message" in data:
                    time.sleep(0.01)
                    yield data["message"]["content"]

    def delete_model(self, model_name: str):
        self.append_log_to_inner_textbox(clear=True)
        if not model_name:
            return
        req = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/delete"),
            data=json.dumps({"name": model_name}).encode("utf-8"),
            method="DELETE",
        )
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    self.append_log_to_inner_textbox("Model deleted successfully.")
                    if model_name == self.loaded_model:
                        self.loaded_model = None
                elif response.status == 404:
                    self.append_log_to_inner_textbox("Model not found.")
        except Exception as e:
            self.append_log_to_inner_textbox(f"Failed to delete model: {e}")
        finally:
            self.update_model_list()
            self.update_model_select()

    def download_model(self, model_name: str, insecure: bool = False):
        self.append_log_to_inner_textbox(clear=True)
        if not model_name:
            return
        self.download_button.config(state="disabled")
        req = urllib.request.Request(
            urllib.parse.urljoin(self.api_url, "/api/pull"),
            data=json.dumps({"name": model_name, "insecure": insecure, "stream": True}).encode("utf-8"),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as response:
                for line in response:
                    data = json.loads(line.decode("utf-8"))
                    log = data.get("error") or data.get("status") or "No response"
                    if "status" in data:
                        total = data.get("total")
                        completed = data.get("completed", 0)
                        if total:
                            log += f" [{completed}/{total}]"
                    self.append_log_to_inner_textbox(log)
                self.loaded_model = model_name
        except Exception as e:
            self.append_log_to_inner_textbox(f"Failed to download model: {e}")
        finally:
            self.update_model_list()
            self.update_model_select()
            if self.download_button.winfo_exists():
                self.download_button.config(state="disabled")

    def clear_chat(self):
        if self.ai_running:
            return
        self.chat_box.delete(1.0, tk.END)
        self.chat_history.clear()
        self.message_index = 0

    def force_clear(self):
        self.chat_box.delete(1.0, tk.END)
        self.chat_history.clear()

    def export_chat_to_pdf(self):
        if not self.chat_history:
            return
        first_three_words = " ".join(self.chat_history[0]['content'].split()[:5]) if self.chat_history[0]['content'] else "Chat"
        file_name = f"{first_three_words}.pdf"
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=file_name)
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            y = height - 50
            styles = getSampleStyleSheet()
            for item in self.chat_history:
                role = item['role']
                content = item['content'].replace('\n', '<br/>').replace('---', '<hr/>')
                html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
                text = f"<p><strong>{role}:</strong> {html_content}</p>"
                p = Paragraph(text, style=styles['Normal'])
                available_width = width - 2 * 50
                available_height = height - 2 * 50
                p_width, p_height = p.wrap(available_width, available_height)
                if y - p_height < 50:
                    c.showPage()
                    y = height - 50
                p.drawOn(c, 50, y - p_height)
                y -= p_height + 20
            c.save()

    def restore_chat_history(self):
        if self.ai_running:
            return
        chats_dir = os.path.join(os.getcwd(), "_chats")
        if not os.path.exists(chats_dir):
            os.makedirs(chats_dir)
        file_path = filedialog.askopenfilename(initialdir=chats_dir, title="Load Chat History",filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            self.loading_messages = True
            Thread(target=self.delayed_loading_messages_reset).start()
            self.force_clear()
            global chat_history
            chat_history = restore_chat_history_from_json(file_path)
            self.chat_history = chat_history
            for item in self.chat_history:
                if item['role'] == 'user':
                    message = item['content']
                    if message:
                        self.append_text_to_chat("You: \n", ("user_label",))
                        self.append_text_to_chat(f"{message}\n\n", ("user",))
                if item['role'] == 'assistant':
                    message = item['content']
                    model_name = item['model']
                    if model_name:
                        self.append_text_to_chat(f"{model_name}\n", ("Bold",))
                    if message:
                        self.append_text_to_chat(message, ("Assistant",))
                    self.append_text_to_chat("\n\n", ("Assistant",))

    def delayed_loading_messages_reset(self):
        time.sleep(1)
        self.loading_messages = False

    def sanitize_filename(self, filename):
        invalid_chars = r'\/:*?"<>|'
        return ''.join('_' if char in invalid_chars else char for char in filename)

    def save_chat_history(self):
        timestamp = time.strftime("TIME_%H_%M_%S_DATE_%d_%m_%Y")
        first_three_words = " ".join(self.chat_history[0]['content'].split()[:5]) if self.chat_history else ""
        file_name = f"{first_three_words}_{timestamp}.json" if first_three_words else f"chat_{timestamp}.json"
        sanitized_file_name = self.sanitize_filename(file_name)
        file_path = os.path.join("_chats", sanitized_file_name)
        with open(file_path, "w") as file:
            json.dump(self.chat_history, file, indent=4)

    def show_error(self, text):
        self.model_select.set(text)
        self.model_select.config(foreground="red")
        self.model_select["values"] = []
        self.send_button.config(state="disabled")

    def show_process_bar(self):
        self.progress.grid(row=0, column=0, sticky="nsew")
        self.stop_button.config(state="normal")
        self.progress.start(10)

    def hide_process_bar(self):
        self.progress.stop()
        self.stop_button.config(state="disabled")
        self.progress.grid_remove()

    def copy_text(self, text: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def append_text_to_chat(self, text: str, *args):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, text, *args)
        if self.ai_running:
            self.chat_box.config(state=tk.DISABLED)

    def append_log_to_inner_textbox(self, message: str = None, clear: bool = False):
        if self.log_textbox.winfo_exists():
            self.log_textbox.config(state=tk.NORMAL)
            if clear:
                self.log_textbox.delete(1.0, tk.END)
            elif message:
                self.log_textbox.insert(tk.END, message + "\n")
        self.log_textbox.config(state=tk.DISABLED)
        self.log_textbox.see(tk.END)

    def update_loaded_model_label(self):
        try:
            result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            lines = result.stdout.strip().split('\n')
            if lines:
                lines = lines[1:]
            loaded_models = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    name = parts[0]
                    model_id = parts[1]
                    size = parts[2]
                    processor = parts[3]
                    until = ' '.join(parts[4:])
                    loaded_models.append({
                        'name': name,
                        'id': model_id,
                        'size': size,
                        'processor': processor,
                        'until': until
                    })
            if loaded_models:
                model_names = ", ".join([model['name'] for model in loaded_models])
                self.loaded_model_label.config(text=f"{model_names}\n")
            else:
                self.loaded_model_label.config(text="No models loaded")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the ollama command: {e}")
            self.loaded_model_label.config(text="Error fetching models")
        except FileNotFoundError:
            print("The ollama command is not found. Please ensure Ollama is installed and in your PATH.")
            self.loaded_model_label.config(text="Ollama command not found")

    def on_closing(self):
        self.root.destroy()
        close("ollama_app")
        close("ollama")

    def free_memory(self):
        self.save_chat_history()
        result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        loaded_models = [line.split()[0] for line in result.stdout.strip().split('\n')[1:] if line]
        for model_name in loaded_models:
            subprocess.run(['ollama', 'stop', model_name], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def on_chat_box_modified(self, event):
        if self.ai_running or self.loading_messages:
            self.user_editing = False
        else:
            self.user_editing = True
        if self.user_editing:
            chat_box_content = self.chat_box.get("1.0", tk.END)
            self.chat_history = convert_input_to_chat_history(chat_box_content)
        self.chat_box.edit_modified(False)

def run():
    global default_font
    root = tk.Tk()
    root.title("Ollama GUI")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"800x600+{(screen_width - 800) // 2}+{(screen_height - 600) // 2}")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=0)
    root.grid_rowconfigure(3, weight=0)
    main_logic = OllamaInterfaceLogic(root)
    gui = GUI(root, main_logic)
    root.state("zoomed")
    root.iconbitmap("icon.ico")
    root.mainloop()

if __name__ == "__main__":
    run()
