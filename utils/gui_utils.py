import tkinter as tk
from tkinter import simpledialog, messagebox

import numpy as np

from deformation.bbw_mesh import BbwMesh
from gui_elements.view_deformation_widget import DeformationWidget


""" Dialog window creation """
class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title, text):
        self.result = None
        self.text = text
        super().__init__(parent, title)

    def body(self, master):
        self.configure(bg="#2E2E2E")  # Dark gray background
        master.configure(bg="#2E2E2E")  # Ensure master frame is also dark

        tk.Label(master, text=self.text,
                 bg="#2E2E2E", fg="white").pack(pady=10)

        self.entry = tk.Entry(master, bg="#3B3B3B", fg="white", insertbackground="white",
                              relief="flat", highlightthickness=0, font=("Arial", 12))
        self.entry.pack(pady=5, padx=10, ipadx=8, ipady=6)

        return self.entry  # Focus on entry field

    def buttonbox(self):
        """Override buttonbox to customize buttons with a dark theme."""
        box = tk.Frame(self, bg="#2E2E2E")  # Dark background
        box.pack(pady=10)  # Add some space below the entry field

        button_style = {
            "bg": "#3B3B3B", "fg": "white", "relief": "flat", "highlightthickness": 0,
            "width": 10, "height": 2, "font": ("Arial", 11, "bold")
        }

        tk.Button(box, text="OK", command=self.ok, **button_style).pack(side="left", padx=10)
        tk.Button(box, text="Cancel", command=self.cancel, **button_style).pack(side="left", padx=10)

    def apply(self):
        self.result = self.entry.get()


""" Window to ask for a file name """
def ask_for_filename(title, text):
    root = tk.Tk()
    root.withdraw()  # Hide main window

    while True:
        dialog = CustomDialog(root, title, text)
        file_name = dialog.result

        if file_name is None:  # User pressed Cancel
            return None

        if file_name.strip():  # Ensure the file name is not empty
            return file_name

        messagebox.showwarning("Save Model", "File name cannot be empty!")


""" Draw a 2D mesh on a canvas """
def draw_mesh(canvas, bbw_mesh: BbwMesh, show_mesh=False):
    # Draw 2D mesh
    if show_mesh:
        for face in bbw_mesh.faces:
            v1 = bbw_mesh.new_vertices[face[0]]
            v2 = bbw_mesh.new_vertices[face[1]]
            v3 = bbw_mesh.new_vertices[face[2]]
            canvas.create_polygon(v1[0], v1[1], v2[0], v2[1], v3[0], v3[1],
                                       outline="darkblue", fill="", width=1)

    # Draw handles
    for index in bbw_mesh.handles_index:
        index = int(index)
        vertex = bbw_mesh.new_vertices[index]
        selected_handle_index = np.where(bbw_mesh.handles_index == index)[0].item()
        rotation = bbw_mesh.handles[selected_handle_index].rotation_matrix

        if selected_handle_index in bbw_mesh.selected_handles_index:
            draw_circle(canvas, vertex[0], vertex[1], color="yellow")
        else:
            draw_circle(canvas, vertex[0], vertex[1], color="red")

        # Draw the rotation vectors
        draw_handle_rotation(canvas, vertex, rotation)


""" Draw a handle on a canvas """
def draw_handle_rotation(canvas, vertex, rotation):
    original_green_vector = np.array([0.0, -20.0])  # Green vector: points upwards (along the y-axis)
    original_blue_vector = np.array([20.0, 0.0])  # Blue vector: points to the right (along the x-axis)

    # Apply the rotation matrix to the original vectors
    rotated_green_vector = rotation @ original_green_vector
    rotated_blue_vector = rotation @ original_blue_vector

    canvas.create_line(vertex[0], vertex[1], vertex[0] + rotated_green_vector[0], vertex[1] + rotated_green_vector[1],
                       fill="lightgreen", width=4)
    canvas.create_line(vertex[0], vertex[1], vertex[0] + rotated_blue_vector[0], vertex[1] + rotated_blue_vector[1],
                       fill="lightblue", width=4)


""" Draw a circle on a canvas """
def draw_circle(canvas, x, y, radius=4, color="blue"):
    canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=color, fill=color, width=1)


""" Create a rendering canvas """
def create_canvas(parent, row, on_resize=None, mouse_press_event=None, mouse_release_event=None,
                  mouse_move_event=None, mouse_wheel_event=None, camera=None):
    canvas = tk.Canvas(parent, bg="#222")
    canvas.bind("<Configure>", on_resize)
    canvas.bind("<ButtonPress-1>", mouse_press_event)
    canvas.bind("<ButtonRelease-1>", mouse_release_event)
    canvas.bind("<B1-Motion>", lambda event: mouse_move_event(event, camera, None))
    canvas.bind("<MouseWheel>", lambda event: mouse_wheel_event(event, camera, None))
    canvas.grid(row=row, column=0, sticky="nsew", padx=5, pady=5)

    return canvas


"""Dynamically arranges buttons in rows based on the frame width."""
def arrange_buttons(frame, button_texts, functions):
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.destroy()

    frame_width = frame.winfo_width()
    button_width = 100
    padding = 10
    max_columns = max(1, frame_width // (button_width + padding))

    col = 0
    row_offset = 1
    for text in button_texts:
        btn = tk.Button(frame, text=text, font=("Arial", 10, "bold"), fg="white", bg="#666", height=2)
        btn.grid(row=row_offset, column=col, padx=5, pady=5, sticky="ew")

        col += 1
        if col >= max_columns:
            col = 0
            row_offset += 1


""" Create a view deformation widget """
def create_view_deformation_widget(scroll_frame, index, manager, widget_management_callback, checkout_callback,
                                   mesh_generation_callback, update_callback):
    widget = DeformationWidget(scroll_frame, manager, index, widget_management_callback, checkout_callback,
                               mesh_generation_callback, update_callback, title=f"Deformation {index + 1}")
    widget.pack(fill="x", padx=5, pady=5)
    return widget
