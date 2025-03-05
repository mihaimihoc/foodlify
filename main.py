import tkinter as tk
from tkinter import messagebox
import json
import os
import accounts

if __name__ == "__main__":
    root = tk.Tk()
    app = accounts.App(root)
    root.mainloop()