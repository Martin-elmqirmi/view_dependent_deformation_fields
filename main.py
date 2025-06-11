import argparse
import tkinter as tk

from gsplat.distributed import cli

from app import App


""" 
    Program entry point
"""
def main(local_rank: int, world_rank, world_size: int, args):
    root = tk.Tk()

    app = App(root)

    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    cli(main, args, verbose=True)