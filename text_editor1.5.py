import tkinter as tk
from tkinter import filedialog, messagebox


class TextEditor:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.geometry("900x600")
        self.file_path = None
        self.dark_mode = False
        self.find_window = None
        self.find_entry = None
        self.replace_entry = None

        self.text = tk.Text(root, wrap="word", undo=True)
        self.text.pack(fill="both", expand=True)
        self.text.focus_set()

        self._build_menu()
        self._bind_shortcuts()
        self._apply_theme()
        self._update_title()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def _build_menu(self) -> None:
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        edit_menu = tk.Menu(menu_bar, tearoff=False)
        view_menu = tk.Menu(menu_bar, tearoff=False)

        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Ctrl+Q")

        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all_text, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.open_find_window, accelerator="Ctrl+F")
        edit_menu.add_command(
            label="Replace...", command=self.open_replace_window, accelerator="Ctrl+H"
        )

        view_menu.add_checkbutton(
            label="Dark Mode",
            command=self.toggle_dark_mode,
            onvalue=True,
            offvalue=False,
        )

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)
        self.root.config(menu=menu_bar)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-S>", lambda event: self.save_as_file())
        self.root.bind("<Control-q>", lambda event: self.exit_app())
        self.root.bind("<Control-f>", lambda event: self.open_find_window())
        self.root.bind("<Control-h>", lambda event: self.open_replace_window())

    def _apply_theme(self) -> None:
        if self.dark_mode:
            text_bg = "#1e1e1e"
            text_fg = "#f3f3f3"
            insert_bg = "#f3f3f3"
            select_bg = "#3d6ea8"
        else:
            text_bg = "#ffffff"
            text_fg = "#000000"
            insert_bg = "#000000"
            select_bg = "#9dc3ff"

        self.text.config(
            bg=text_bg,
            fg=text_fg,
            insertbackground=insert_bg,
            selectbackground=select_bg,
        )

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

    def cut_text(self) -> None:
        self.text.event_generate("<<Cut>>")

    def copy_text(self) -> None:
        self.text.event_generate("<<Copy>>")

    def paste_text(self) -> None:
        self.text.event_generate("<<Paste>>")

    def select_all_text(self) -> None:
        self.text.tag_add("sel", "1.0", tk.END)
        self.text.mark_set(tk.INSERT, "1.0")
        self.text.see(tk.INSERT)

    def open_find_window(self) -> None:
        self._open_search_window(with_replace=False)

    def open_replace_window(self) -> None:
        self._open_search_window(with_replace=True)

    def _open_search_window(self, with_replace: bool) -> None:
        if self.find_window and self.find_window.winfo_exists():
            self.find_window.lift()
            if self.find_entry:
                self.find_entry.focus_set()
            return

        self.find_window = tk.Toplevel(self.root)
        self.find_window.title("Find and Replace" if with_replace else "Find")
        self.find_window.transient(self.root)
        self.find_window.resizable(False, False)

        tk.Label(self.find_window, text="Find:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.find_entry = tk.Entry(self.find_window, width=32)
        self.find_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.find_entry.focus_set()

        tk.Button(self.find_window, text="Find Next", command=self.find_next).grid(
            row=0, column=2, padx=8, pady=8
        )

        if with_replace:
            tk.Label(self.find_window, text="Replace:").grid(
                row=1, column=0, padx=8, pady=8, sticky="w"
            )
            self.replace_entry = tk.Entry(self.find_window, width=32)
            self.replace_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

            tk.Button(self.find_window, text="Replace", command=self.replace_one).grid(
                row=1, column=2, padx=8, pady=8
            )
            tk.Button(self.find_window, text="Replace All", command=self.replace_all).grid(
                row=2, column=2, padx=8, pady=8
            )
        else:
            self.replace_entry = None

        self.find_window.grid_columnconfigure(1, weight=1)
        self.find_window.bind("<Return>", lambda event: self.find_next())
        self.find_window.bind("<Escape>", lambda event: self.find_window.destroy())

    def find_next(self) -> None:
        if not self.find_entry:
            return

        query = self.find_entry.get()
        if not query:
            return

        start = self.text.index(tk.INSERT)
        match_start = self.text.search(query, start, stopindex=tk.END)
        if not match_start:
            match_start = self.text.search(query, "1.0", stopindex=tk.END)
            if not match_start:
                messagebox.showinfo("Find", f'"{query}" was not found.')
                return

        match_end = f"{match_start}+{len(query)}c"
        self.text.tag_remove("sel", "1.0", tk.END)
        self.text.tag_add("sel", match_start, match_end)
        self.text.mark_set(tk.INSERT, match_end)
        self.text.see(match_start)
        self.text.focus_set()

    def replace_one(self) -> None:
        if not self.find_entry or not self.replace_entry:
            return

        query = self.find_entry.get()
        replacement = self.replace_entry.get()
        if not query:
            return

        try:
            selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selection = ""

        if selection == query:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, replacement)

        self.find_next()

    def replace_all(self) -> None:
        if not self.find_entry or not self.replace_entry:
            return

        query = self.find_entry.get()
        replacement = self.replace_entry.get()
        if not query:
            return

        count = 0
        index = "1.0"
        while True:
            match_start = self.text.search(query, index, stopindex=tk.END)
            if not match_start:
                break
            match_end = f"{match_start}+{len(query)}c"
            self.text.delete(match_start, match_end)
            self.text.insert(match_start, replacement)
            index = f"{match_start}+{len(replacement)}c"
            count += 1

        messagebox.showinfo("Replace All", f"Replaced {count} occurrence(s).")

    def toggle_dark_mode(self) -> None:
        self.dark_mode = not self.dark_mode
        self._apply_theme()

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
