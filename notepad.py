import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import speech_recognition as sr
from spellchecker import SpellChecker
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Mini Notepad")
        self.root.geometry("900x600")

        # Dark Mode Colors
        self.light_bg = "white"
        self.dark_bg = "#2b2b2b"
        self.light_fg = "black"
        self.dark_fg = "white"

        self.is_dark_mode = False
        self.current_file = None
        self.spell = SpellChecker()

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        # Menu Bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=lambda: self.text_area.event_generate("<<Undo>>"))
        edit_menu.add_command(label="Redo", command=lambda: self.text_area.event_generate("<<Redo>>"))
        edit_menu.add_separator()
        
        edit_menu.add_command(label="Find & Replace", command=self.find_replace)
        edit_menu.add_command(label="Check Spelling", command=self.check_spelling)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # View Menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # Tools Menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        tools_menu.add_command(label="Voice to Text", command=self.voice_to_text)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)

        # Tabs for Multiple Files
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both")
        self.new_tab()

        # Status Bar
        self.status_bar = tk.Label(self.root, text="Words: 0 | Characters: 0", anchor="e")
        self.status_bar.pack(fill="x")

    def new_tab(self):
        frame = tk.Frame(self.tab_control)
        self.text_area = tk.Text(frame, wrap="word", undo=True, font=("Arial", 12))
        self.text_area.pack(expand=1, fill="both", padx=5, pady=5)
        self.text_area.bind("<KeyRelease>", self.update_word_count)
        self.tab_control.add(frame, text="Untitled")
        self.tab_control.select(frame)

    def new_file(self):
        self.new_tab()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, content)
            self.current_file = file_path

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.current_file = file_path

    def find_replace(self):
        find_replace_window = tk.Toplevel(self.root)
        find_replace_window.title("Find & Replace")
        find_replace_window.geometry("300x150")

        tk.Label(find_replace_window, text="Find:").grid(row=0, column=0)
        tk.Label(find_replace_window, text="Replace:").grid(row=1, column=0)

        find_entry = tk.Entry(find_replace_window, width=25)
        find_entry.grid(row=0, column=1)
        replace_entry = tk.Entry(find_replace_window, width=25)
        replace_entry.grid(row=1, column=1)

        def replace_text():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            content = self.text_area.get(1.0, tk.END)
            new_content = content.replace(find_text, replace_text)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, new_content)

        tk.Button(find_replace_window, text="Replace", command=replace_text).grid(row=2, column=1, pady=5)

    def check_spelling(self):
        text_content = self.text_area.get(1.0, tk.END).split()
        incorrect_words = [word for word in text_content if word not in self.spell]
        
        messagebox.showinfo("Spell Check", f"Incorrect Words:\n{', '.join(incorrect_words)}")

    def voice_to_text(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            messagebox.showinfo("Voice to Text", "Speak now...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            self.text_area.insert(tk.END, text)
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand the audio")
        except sr.RequestError:
            messagebox.showerror("Error", "Could not request results")

    def update_word_count(self, event=None):
        text_content = self.text_area.get(1.0, tk.END)
        words = len(text_content.split())
        characters = len(text_content) - 1
        self.status_bar.config(text=f"Words: {words} | Characters: {characters}")

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        bg_color = self.dark_bg if self.is_dark_mode else self.light_bg
        fg_color = self.dark_fg if self.is_dark_mode else self.light_fg
        self.text_area.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = NotepadApp(root)
    root.mainloop()  