import tkinter as tk
from tkinter import filedialog, messagebox


class TextEditor:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.geometry("900x600")
        self.file_path = None

        self.text = tk.Text(root, wrap="word", undo=True)
        self.text.pack(fill="both", expand=True)
        self.text.focus_set()

        self._build_menu()
        self._bind_shortcuts()
        self._update_title()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=False)

        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Ctrl+Q")

        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-S>", lambda event: self.save_as_file())
        self.root.bind("<Control-q>", lambda event: self.exit_app())

    def _update_title(self) -> None:
        name = self.file_path if self.file_path else "Untitled"
        self.root.title(f"{name} - TXT Editor")

    def _has_unsaved_changes(self) -> bool:
        return self.text.edit_modified()

    def _confirm_discard_changes(self) -> bool:
        if not self._has_unsaved_changes():
            return True

        answer = messagebox.askyesnocancel(
            "Unsaved Changes",
            "You have unsaved changes. Save before continuing?",
        )

        if answer is None:
            return False
        if answer:
            return self.save_file()
        return True

    def new_file(self) -> None:
        if not self._confirm_discard_changes():
            return

        self.text.delete("1.0", tk.END)
        self.file_path = None
        self.text.edit_modified(False)
        self._update_title()

    def open_file(self) -> None:
        if not self._confirm_discard_changes():
            return

        selected = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not selected:
            return

        try:
            with open(selected, "r", encoding="utf-8") as file:
                content = file.read()
        except OSError as error:
            messagebox.showerror("Open Error", f"Could not open file:\n{error}")
            return

        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.file_path = selected
        self.text.edit_modified(False)
        self._update_title()

    def save_file(self) -> bool:
        if not self.file_path:
            return self.save_as_file()

        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                file.write(self.text.get("1.0", tk.END).rstrip("\n"))
        except OSError as error:
            messagebox.showerror("Save Error", f"Could not save file:\n{error}")
            return False

        self.text.edit_modified(False)
        self._update_title()
        return True

    def save_as_file(self) -> bool:
        selected = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not selected:
            return False

        self.file_path = selected
        return self.save_file()

    def exit_app(self) -> None:
        if not self._confirm_discard_changes():
            return
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    TextEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
