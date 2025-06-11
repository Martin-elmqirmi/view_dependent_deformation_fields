import os
import tkinter as tk
from abc import ABC, abstractmethod
from PIL import Image, ImageTk
from windows.rendering_window import RenderingWindow


class AbstractModelWindow(tk.Frame, ABC):
    BUTTON_SIZE = 150
    PADDING = 20

    def __init__(self, parent, model_dir, image_dir, file_ext, render_type):
        super().__init__(parent, bg="#1a1a1a")
        self.model_dir = model_dir
        self.image_dir = image_dir
        self.file_ext = file_ext
        self.render_type = render_type
        os.makedirs(self.image_dir, exist_ok=True)

        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0)
        self.scroll_frame = tk.Frame(self.canvas, bg="#1a1a1a")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.models = []
        self.load_models()

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.render_buttons())

        # Bind mouse wheel events
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_models(self):
        self.models.clear()
        for file in os.listdir(self.model_dir):
            if file.endswith(self.file_ext):
                image_name = f"{os.path.splitext(file)[0]}.png"
                image_path = os.path.join(self.image_dir, image_name)
                model_path = os.path.join(self.model_dir, file)
                if not os.path.exists(image_path):
                    self.render_model(model_path, image_path)

                self.models.append((file, image_path))

    def render_buttons(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            self.after(100, self.render_buttons)
            return

        total_button_width = self.BUTTON_SIZE + self.PADDING
        columns = max((canvas_width - self.PADDING) // total_button_width, 1) - 1

        for idx, (model_name, image_path) in enumerate(self.models):
            row = idx // columns
            col = idx % columns
            self.add_model_button(model_name, image_path, row, col)

    def add_model_button(self, model_name, image_path, row, col):
        img = Image.open(image_path).resize((self.BUTTON_SIZE, self.BUTTON_SIZE))
        photo = ImageTk.PhotoImage(img)

        frame = tk.Frame(self.scroll_frame, bg="#1a1a1a")
        frame.grid(row=row, column=col, padx=self.PADDING // 2, pady=self.PADDING // 2)

        button = tk.Button(frame, image=photo,
                           command=lambda p=os.path.join(self.model_dir, model_name): self.select_model(p),
                           bd=0, bg="black")
        button.image = photo
        button.pack(side="top")

        text_overlay = tk.Label(frame, text=model_name, font=("Arial", 12, "bold"),
                                fg="white", bg="#3a3a3a", width=20)
        text_overlay.pack(side="top", fill="x")

    def select_model(self, path):
        RenderingWindow(self.master, path, self.render_type, None)

    @abstractmethod
    def render_model(self, model_path, image_path):
        pass
