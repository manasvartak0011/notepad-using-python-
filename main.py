import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font

class Notepad(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notepad")
        self.geometry("800x600")

        # Track current open file
        self.current_file = None
        self.text_changed = False

        # Set up font
        self.font_family = "Consolas"
        self.font_size = 12
        self.text_font = font.Font(family=self.font_family, size=self.font_size)

        # Create toolbar
        self.create_toolbar()

        # Create Text widget with scrollbar
        self.text = tk.Text(self, wrap="word", undo=True, font=self.text_font)
        self.text.pack(fill="both", expand=True, side="left")
        self.text.bind("<<Modified>>", self.on_text_change)

        scrollbar = tk.Scrollbar(self, command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scrollbar.set)

        # Create menu
        self.create_menu()

        # Create status bar
        self.status_bar = tk.Label(self, text="Line 1, Column 1", anchor="e")
        self.status_bar.pack(fill="x", side="bottom")

        self.text.bind('<KeyRelease>', self.update_status_bar)

        # Keyboard shortcuts
        self.bind_shortcuts()

    def create_toolbar(self):
        toolbar = tk.Frame(self, bd=1, relief="raised")
        toolbar.pack(side="top", fill="x")

        btn_specs = [
            ("New", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file),
            ("Cut", self.cut),
            ("Copy", self.copy),
            ("Paste", self.paste),
            ("Find", self.find_text),
            ("Undo", self.undo),
            ("Redo", self.redo),
        ]
        for (text, cmd) in btn_specs:
            btn = tk.Button(toolbar, text=text, command=cmd)
            btn.pack(side="left", padx=2, pady=2)

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

        edit_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")

        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-f>", lambda e: self.find_text())
        self.bind("<Control-a>", lambda e: self.select_all())
        self.bind("<Control-x>", lambda e: self.cut())
        self.bind("<Control-c>", lambda e: self.copy())
        self.bind("<Control-v>", lambda e: self.paste())
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())

    def on_text_change(self, event=None):
        if self.text.edit_modified():
            self.text_changed = True
            self.text.edit_modified(False)
            self.update_status_bar()

    def update_status_bar(self, event=None):
        row, col = self.text.index("insert").split(".")
        self.status_bar.config(text=f"Line {int(row)}, Column {int(col)+1}")

    def new_file(self):
        if self.text_changed and not self.ask_save_changes():
            return
        self.text.delete("1.0", "end")
        self.current_file = None
        self.title("Notepad")
        self.text_changed = False

    def open_file(self):
        if self.text_changed and not self.ask_save_changes():
            return
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
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def ask_save_changes(self):
        answer = messagebox.askyesnocancel("Save Changes?", "You have unsaved changes. Save before continuing?")
        if answer:  # yes
            self.save_file()
            return True
        elif answer is False:  # no
            return True
        else:  # cancel
            return False

    def exit_app(self):
        if self.text_changed and not self.ask_save_changes():
            return
        self.destroy()

    def cut(self):
        self.text.event_generate("<<Cut>>")

    def copy(self):
        self.text.event_generate("<<Copy>>")

    def paste(self):
        self.text.event_generate("<<Paste>>")

    def undo(self):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass

    def select_all(self):
        self.text.tag_add("sel", "1.0", "end")

    def find_text(self):
        find_string = simpledialog.askstring("Find", "Enter text to find:")
        if find_string:
            start_pos = "1.0"
            while True:
                start_pos = self.text.search(find_string, start_pos, stopindex="end")
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(find_string)}c"
                self.text.tag_add("found", start_pos, end_pos)
                self.text.tag_config("found", background="yellow")
                start_pos = end_pos

    def show_about(self):
        messagebox.showinfo("About Notepad", "Notepad Application\nCreated by Your Name\nGitHub: https://github.com/yourusername")

if __name__ == "__main__":
    app = Notepad()
    app.mainloop()
