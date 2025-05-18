import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font, colorchooser
import os, json, datetime
import pyttsx3

class Notepad(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notepad")
        self.geometry("900x650")

        self.current_file = None
        self.text_changed = False
        self.recent_files = []
        self.auto_save_enabled = False
        self.preferences_file = "preferences.json"

        self.font_family = "Consolas"
        self.font_size = 12
        self.text_font = font.Font(family=self.font_family, size=self.font_size)

        self.create_toolbar()
        self.create_text_widget()
        self.create_menu()
        self.create_status_bar()

        self.load_preferences()

        self.text.bind("<<Modified>>", self.on_text_change)
        self.bind_shortcuts()

    def create_toolbar(self):
        toolbar = tk.Frame(self, bd=1, relief="raised")
        toolbar.pack(side="top", fill="x")
        btn_specs = [
            ("New", self.new_file), ("Open", self.open_file), ("Save", self.save_file),
            ("Cut", self.cut), ("Copy", self.copy), ("Paste", self.paste),
            ("Find", self.find_text), ("Replace", self.replace_text),
            ("Font", self.choose_font), ("Dark Mode", self.toggle_dark_mode),
            ("Speak", self.speak_text), ("Insert Date", self.insert_date)
        ]
        for (text, cmd) in btn_specs:
            btn = tk.Button(toolbar, text=text, command=cmd)
            btn.pack(side="left", padx=2, pady=2)

    def create_text_widget(self):
        self.text = tk.Text(self, wrap="word", undo=True, font=self.text_font)
        self.text.pack(fill="both", expand=True, side="left")
        scrollbar = tk.Scrollbar(self, command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scrollbar.set)

    def create_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)

        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_files_menu()

        edit_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit_menu)
        for action, command in [
            ("Undo", self.undo), ("Redo", self.redo),
            ("Cut", self.cut), ("Copy", self.copy), ("Paste", self.paste),
            ("Find", self.find_text), ("Replace", self.replace_text),
            ("Select All", self.select_all)
        ]:
            edit_menu.add_command(label=action, command=command)

        tools_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Auto Save", command=self.toggle_auto_save)
        tools_menu.add_command(label="Text to Speech", command=self.speak_text)

        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_status_bar(self):
        self.status_bar = tk.Label(self, text="Line 1, Column 1 | Words: 0 | Chars: 0", anchor="e")
        self.status_bar.pack(fill="x", side="bottom")
        self.text.bind('<KeyRelease>', self.update_status_bar)

    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-f>", lambda e: self.find_text())
        self.bind("<Control-a>", lambda e: self.select_all())
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())

    def on_text_change(self, event=None):
        if self.text.edit_modified():
            self.text_changed = True
            self.text.edit_modified(False)
            self.update_status_bar()

    def update_status_bar(self, event=None):
        row, col = self.text.index("insert").split(".")
        content = self.text.get("1.0", "end-1c")
        word_count = len(content.split())
        char_count = len(content)
        self.status_bar.config(text=f"Line {int(row)}, Col {int(col)+1} | Words: {word_count} | Chars: {char_count}")

    def new_file(self):
        if self.text_changed and not self.ask_save_changes():
            return
        self.text.delete("1.0", "end")
        self.current_file = None
        self.title("Notepad")
        self.text_changed = False

    def open_file(self):
        file = filedialog.askopenfilename(defaultextension=".txt",
                                          filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            self.current_file = file
            self.title(f"{file} - Notepad")
            self.text_changed = False
            self.add_to_recent_files(file)

    def save_file(self):
        if self.current_file:
            try:
                content = self.text.get("1.0", "end-1c")
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.text_changed = False
                self.title(f"{self.current_file} - Notepad")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if file:
            try:
                content = self.text.get("1.0", "end-1c")
                with open(file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.current_file = file
                self.text_changed = False
                self.title(f"{file} - Notepad")
                self.add_to_recent_files(file)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def add_to_recent_files(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:5]
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        self.recent_menu.delete(0, "end")
        for file in self.recent_files:
            self.recent_menu.add_command(label=file, command=lambda f=file: self.open_recent_file(f))

    def open_recent_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            self.current_file = file_path
            self.title(f"{file_path} - Notepad")
            self.text_changed = False
        else:
            messagebox.showerror("Error", "File not found.")

    def toggle_auto_save(self):
        self.auto_save_enabled = not self.auto_save_enabled
        if self.auto_save_enabled:
            self.auto_save()

    def auto_save(self):
        if self.auto_save_enabled and self.current_file:
            self.save_file()
        self.after(5000, self.auto_save)

    def toggle_dark_mode(self):
        bg, fg = ("#1e1e1e", "#c0c0c0") if self.text["background"] == "white" else ("white", "black")
        self.text.config(bg=bg, fg=fg)

    def choose_font(self):
        new_size = simpledialog.askinteger("Font Size", "Enter font size:", initialvalue=self.font_size)
        if new_size:
            self.font_size = new_size
            self.text_font.config(size=self.font_size)
            self.save_preferences()

    def find_text(self):
        find_string = simpledialog.askstring("Find", "Enter text to find:")
        if find_string:
            self.text.tag_remove("found", "1.0", "end")
            start_pos = "1.0"
            while True:
                start_pos = self.text.search(find_string, start_pos, stopindex="end")
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(find_string)}c"
                self.text.tag_add("found", start_pos, end_pos)
                self.text.tag_config("found", background="yellow")
                start_pos = end_pos

    def replace_text(self):
        find_string = simpledialog.askstring("Find", "Find:")
        replace_string = simpledialog.askstring("Replace", "Replace with:")
        if find_string and replace_string is not None:
            content = self.text.get("1.0", "end-1c").replace(find_string, replace_string)
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)

    def insert_date(self):
        self.text.insert("insert", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def speak_text(self):
        engine = pyttsx3.init()
        engine.say(self.text.get("1.0", "end-1c"))
        engine.runAndWait()

    def ask_save_changes(self):
        answer = messagebox.askyesnocancel("Save Changes?", "You have unsaved changes. Save before continuing?")
        if answer:
            self.save_file()
            return True
        elif answer is False:
            return True
        else:
            return False

    def exit_app(self):
        if self.text_changed and not self.ask_save_changes():
            return
        self.save_preferences()
        self.destroy()

    def save_preferences(self):
        prefs = {"font_size": self.font_size}
        with open(self.preferences_file, "w") as f:
            json.dump(prefs, f)

    def load_preferences(self):
        if os.path.exists(self.preferences_file):
            with open(self.preferences_file, "r") as f:
                prefs = json.load(f)
            self.font_size = prefs.get("font_size", 12)
            self.text_font.config(size=self.font_size)

    def cut(self): self.text.event_generate("<<Cut>>")
    def copy(self): self.text.event_generate("<<Copy>>")
    def paste(self): self.text.event_generate("<<Paste>>")
    def undo(self): self.text.edit_undo()
    def redo(self): self.text.edit_redo()
    def select_all(self): self.text.tag_add("sel", "1.0", "end")
    def show_about(self):
        messagebox.showinfo("About Notepad", "Advanced Notepad by Your Name\nGitHub: https://github.com/yourusername")

if __name__ == "__main__":
    app = Notepad()
    app.mainloop()
