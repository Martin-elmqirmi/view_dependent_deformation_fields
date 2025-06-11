import tkinter as tk

from windows.gsplat_window import GsplatWindow
from windows.mesh_window import MeshWindow
from windows.vd_gsplat_window import VDGsplatWindow
from windows.vd_mesh_window import VDMeshWindow


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Renderer Selection")
        self.root.geometry("1600x900")  # Increased window size
        self.root.configure(background="#2b2b2b")

        title_font = ("Arial", 18, "bold")
        button_font = ("Arial", 14, "bold")
        button_bg = "#4CAF50"
        button_fg = "white"

        main_frame = tk.Frame(root, bg="#2b2b2b")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Configure grid: 2 rows, 2 columns
        for i in range(2):
            main_frame.columnconfigure(i, weight=1)
            main_frame.rowconfigure(i, weight=1)

        # Section 1: 3D Gaussian Splatting
        frame_gsplat = tk.Frame(main_frame, bg="#2b2b2b", bd=2, relief="groove")
        frame_gsplat.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(frame_gsplat, text="3D Gaussian Splatting", font=title_font, fg="white", bg="#2b2b2b").pack(pady=10)
        GsplatWindow(frame_gsplat, "models/gsplat").pack(pady=10, fill="both", expand=True)

        # Section 2: 3D Meshes
        frame_mesh = tk.Frame(main_frame, bg="#2b2b2b", bd=2, relief="groove")
        frame_mesh.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(frame_mesh, text="3D Meshes", font=title_font, fg="white", bg="#2b2b2b").pack(pady=10)
        MeshWindow(frame_mesh, "models/meshes").pack(pady=10, fill="both", expand=True)

        # Section 3: View-Dependent Gaussian Splatting
        frame_vd_gsplat = tk.Frame(main_frame, bg="#2b2b2b", bd=2, relief="groove")
        frame_vd_gsplat.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(frame_vd_gsplat, text="View-Dependent Gaussian Splatting", font=title_font, fg="white",
                 bg="#2b2b2b").pack(pady=10)
        VDGsplatWindow(frame_vd_gsplat, "models/vd_gsplat").pack(pady=10, fill="both", expand=True)

        # Section 4: View-Dependent Meshes
        frame_vd_mesh = tk.Frame(main_frame, bg="#2b2b2b", bd=2, relief="groove")
        frame_vd_mesh.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(frame_vd_mesh, text="View-Dependent Meshes", font=title_font, fg="white", bg="#2b2b2b").pack(pady=10)
        VDMeshWindow(frame_vd_mesh, "models/vd_meshes").pack(pady=10, fill="both", expand=True)
