import customtkinter as ctk
import os
#this part was fully written by ai because im lazy ass

class InputDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Input Dialog", prompt="Enter name", default_text=""):
        super().__init__(master)
        self.result = None

        self.title(title)
        self.geometry("400x150")
        current_directory = os.path.dirname(os.path.abspath(__file__))

        self.after(200, lambda: self.iconbitmap(os.path.join(current_directory, "icon.ico")))
        self.resizable(False, False)

        # Center the dialog on the screen
        self.center_window()

        # Prompt Label
        self.label = ctk.CTkLabel(self, text=prompt)
        self.label.pack(pady=(20, 10))

        # Entry Box
        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=5)

        # Set default text
        self.entry.insert(0, default_text)

        # Buttons Frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        self.ok_button = ctk.CTkButton(self.button_frame, text="OK", command=self.on_ok, fg_color="#1F1F1F", hover_color="#262626")
        self.ok_button.pack(side="left", padx=5, pady=5)

        # Cancel Button
        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.on_cancel, fg_color="#1F1F1F", hover_color="#262626")
        self.cancel_button.pack(side="left", padx=5, pady=5)

    def center_window(self):
        """Centers the window on the screen."""
        self.update_idletasks()  # Update geometry information
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2  # Center horizontally
        y = (screen_height - 150) // 2  # Center vertically
        self.geometry(f"400x150+{x}+{y}")

    def on_ok(self):
        self.result = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

    @staticmethod
    def show(master, title="Input Dialog", prompt="Enter name of the new collection", default_text=""):
        dialog = InputDialog(master, title, prompt, default_text)
        dialog.grab_set()
        dialog.wait_window()
        return dialog.result