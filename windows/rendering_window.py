import tkinter as tk
from tkinter import ttk

from camera.abstract_camera import AbstractCamera
from manager import Manager
from utils.gui_utils import create_view_deformation_widget

""" Rendering window for both Gsplat and Meshes including :
    - Functions to get the user actions on the screen
    - Have all the buttons to build the view-dependent model
"""
class RenderingWindow:
    def __init__(self, parent, data_path, renderer_type, data=None):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Rendering Window - {data_path}")
        self.window.geometry("1200x700")
        self.window.configure(bg="#1a1a1a")

        # Initialize the manager for the rendering and the deformations
        self.manager = Manager(data_path, renderer_type, data)

        # ---- GRID CONFIGURATION ----
        self.window.columnconfigure(0, weight=1)  # Big render area (Expands)
        self.window.columnconfigure(1, weight=0)  # Scrollable Frame (Fixed width)
        self.window.rowconfigure(0, weight=3)     # Rendering areas (Expands)
        self.window.rowconfigure(1, weight=0)     # Deformation Buttons (Fixed height)
        self.window.rowconfigure(2, weight=0)     # Video Buttons (Fixed height)

        # ---- Big Rendering Area (Expands) ----
        self.big_render_frame = tk.Frame(self.window, bg="black")
        self.big_render_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.big_render_frame.columnconfigure(0, weight=1)
        self.big_render_frame.rowconfigure(0, weight=1)

        self.big_render_canvas = tk.Canvas(self.big_render_frame, bg="black")
        self.big_render_canvas.grid(row=0, column=0, sticky="nsew")
        self.big_render_canvas.bind("<Configure>", self.on_deformation_resize)
        self.big_render_canvas.bind("<ButtonPress-1>", self.mouse_press_event)
        self.big_render_canvas.bind("<B1-Motion>", lambda event: self.mouse_move_event(event, self.manager.deformation_camera))
        self.big_render_canvas.bind("<ButtonRelease-1>", self.mouse_release_event)
        self.big_render_canvas.bind("<MouseWheel>", lambda event: self.mouse_wheel_event(event, self.manager.deformation_camera))

        # ---- Scrollable Frame (Fixed Width) ----
        self.scroll_frame_container = tk.Frame(self.window, width=350, bg="#222")
        self.scroll_frame_container.grid(row=0, column=1, rowspan=3, sticky="nsw", padx=5, pady=5)
        self.scroll_frame_container.grid_propagate(False)

        self.scroll_frame = self.create_scrollable_frame()
        self.scroll_frame.pack(fill="both", expand=True)

        self.view_deformation_widgets = []

        # ---- Button Sections (BOTTOM) ----
        self.create_button_section("Deformation Functions", ["New View Deformation", "Move Handles",
                                                             "Save View Deformation", "Save model", "Show 2D mesh"],
                                   row=1, columnspan=1)
        self.create_button_section("Video Functions", [], row=2, columnspan=1)

        self.update_deformation_widgets()
        self.update()

    """ Create the scroll frame """
    def create_scrollable_frame(self):
        canvas = tk.Canvas(self.scroll_frame_container, bg="#222", width=350, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.scroll_frame_container, orient="vertical", command=canvas.yview)

        scrollable_frame = tk.Frame(canvas, bg="#222")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame

    """ Update the view deformation widgets when deleting a view deformation """
    def update_deformation_widgets(self):
        for widget in self.view_deformation_widgets:
            widget.destroy()

        for i, view_deformation in enumerate(self.manager.view_deformer.view_deformations):
            widget = create_view_deformation_widget(
                self.scroll_frame,
                i,
                self.manager,
                self.update_deformation_widgets,
                self.checkout_view_deformation,
                self.mesh_generation_callback,
                self.update
            )
            self.view_deformation_widgets.append(widget)

    """ Checkout the viewpoint associated with the ith view deformation """
    def checkout_view_deformation(self, i):
        self.manager.checkout_view_deformation(i)
        self.update()

    """ Generate the 2D mesh for the ith view deformation """
    def mesh_generation_callback(self, i):
        self.manager.mesh_generation_callback(i)
        self.update()

    """ Create a button section """
    def create_button_section(self, title, button_texts, row, columnspan):
        frame = tk.Frame(self.window, bg="#333")
        frame.grid(row=row, column=0, columnspan=columnspan, sticky="ew", padx=5, pady=5)

        tk.Label(frame, text=title, fg="white", bg="#333").grid(row=0, column=0, columnspan=100, sticky="w")

        button_functions = {
            "New View Deformation": self.new_view_deformation,
            "Move Handles": self.move_handles,
            "Save View Deformation": self.save_view_deformation,
            "Save model": self.save_model,
            "Show 2D mesh": self.show_2d_mesh
        }

        for i, text in enumerate(button_texts):
            if text in button_functions:
                btn = tk.Button(frame, text=text, command=button_functions[text], bg="#444", fg="white")
                btn.grid(row=1, column=i, padx=5, pady=5, sticky="ew")

    """ Save a view deformation allowing to move around the object """
    def save_view_deformation(self):
        if self.manager.view_deformation is not None:
            self.manager.view_deformer.view_deformations[self.manager.view_deformation].need_update = True
            self.update()
            self.view_deformation_widgets[self.manager.view_deformation].hide_mesh_button()
        self.manager.save_view_deformation()
        self.update()

    """ Allow the user to move the handles """
    def move_handles(self):
        self.manager.move_handles()

    """ Save the view-dependent model """
    def save_model(self):
        print("save_model!")
        self.manager.save_model()

    """ Allows the user to show or hide the 2D mesh on the screen """
    def show_2d_mesh(self):
        print("show_2d_mesh!")
        self.manager.show_mesh = not self.manager.show_mesh
        self.update()

    """ Create a new view deformation """
    def new_view_deformation(self):
        index = self.manager.new_view_deformation()

        widget = create_view_deformation_widget(
            self.scroll_frame,
            index,
            self.manager,
            self.update_deformation_widgets,
            self.checkout_view_deformation,
            self.mesh_generation_callback,
            self.update
        )
        self.view_deformation_widgets.append(widget)
        widget.pack(fill=tk.X, padx=10, pady=5)
        self.update()

    """ Resize the deformation screen """
    def on_deformation_resize(self, event):
        new_width = event.width
        new_height = event.height
        self.manager.on_deformation_resize(new_width, new_height)
        self.update()

    """ On mouse press event """
    def mouse_press_event(self, event):
        self.manager.mouse_press_event(event)
        self.update()

    """ On mouse move event """
    def mouse_move_event(self, event, camera: AbstractCamera):
        self.manager.mouse_move_event(event, camera)
        self.update()

    """ On mouse release event """
    def mouse_release_event(self, event):
        self.manager.mouse_release_event(event)
        self.update()

    """ On mouse wheel event """
    def mouse_wheel_event(self, event, camera: AbstractCamera):
        self.manager.mouse_wheel_event(event, camera)
        self.update()

    """ update the rendering window """
    def update(self):
        self.big_render_canvas.delete("all")
        self.manager.update(self.big_render_canvas)
