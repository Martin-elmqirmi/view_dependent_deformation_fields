import tkinter as tk

from gui_elements.numeric_input import NumericInput


""" View Deformation Widget """
class DeformationWidget(tk.Frame):
    def __init__(self, parent, manager, index, widget_management_callback, checkout_callback, generate_mesh_callback,
                 update_callback, title="Unknown",
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent  # Store reference to parent for deletion
        self.configure(bg="#333", padx=3, pady=3, bd=2, relief="ridge")
        view_deformation = manager.view_deformer.view_deformations[index]

        # Title Bar (Title + Close Button)
        title_bar = tk.Frame(self, bg="#444")
        title_bar.pack(fill="x", padx=2, pady=2)

        self.title_label = tk.Label(title_bar, text=title, bg="#444", fg="white", font=("Arial", 9, "bold"))
        self.title_label.pack(side="left", padx=2)

        self.close_button = tk.Button(title_bar, text="❌", command=lambda: self.close_widget(manager, index,
                                                                                             widget_management_callback,
                                                                                             update_callback),
                                      bg="#900", fg="white", width=2, height=1)
        self.close_button.pack(side="right", padx=2)

        # Azimuth Control
        self.azimuth = NumericInput(self, view_deformation.change_variance_azimuth, update_callback, label="Azimuth",
                                    min_val=0, max_val=80, step=1, initial=view_deformation.variance_azimuth)
        self.azimuth.pack(fill="x", padx=3, pady=1)

        # Polar Control
        self.polar = NumericInput(self, view_deformation.change_variance_polar, update_callback, label="Polar",
                                  min_val=0, max_val=80, step=1, initial=view_deformation.variance_polar)
        self.polar.pack(fill="x", padx=3, pady=1)

        # 2D Mesh Button
        self.mesh_button = tk.Button(self, text="Generate 2D mesh", bg="#666", fg="white",
                                         command=lambda: self.on_mesh_click(generate_mesh_callback, index,
                                                                            update_callback), height=1)
        self.mesh_button.pack(fill="x", padx=3, pady=(5, 1))  # You can tweak padding here

        # Action Button
        self.checkout_button = tk.Button(self, text="Checkout view deformation", bg="#555", fg="white",
                                       command=lambda: self.on_checkout_click(checkout_callback, index, update_callback),
                                       height=1)
        self.checkout_button.pack(fill="x", padx=3, pady=3)

    """ Remove the view deformation """
    def close_widget(self, manager, index, widget_management_callback, update_callback):
        manager.delete_view_deformation(index)
        widget_management_callback()
        self.destroy()
        update_callback()

    """ Checkout the view deformation """
    def on_checkout_click(self, checkout_callback, index, update_callback):
        checkout_callback(index)
        print(f"Azimuth: {self.azimuth.value.get()}, Polar: {self.polar.value.get()}")
        update_callback()

    """ Generate the 2D mesh of the view deformation """
    def on_mesh_click(self, generate_mesh_callback, index, update_callback):
        generate_mesh_callback(index)
        print("Optional button clicked")
        update_callback()

    """ Show the generate 2D mesh button """
    def show_mesh_button(self):
        self.mesh_button.pack(fill="x", padx=3, pady=(5, 1))

    """ Hide the generate 2D mesh button """
    def hide_mesh_button(self):
        self.mesh_button.pack_forget()