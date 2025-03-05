import tkinter as tk
import webbrowser
from tkinter import messagebox
import json
import os
import re
from menu import MenuApp

ACCOUNTS_FILE = "accounts.json"


def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return {}
    try:
        with open(ACCOUNTS_FILE, "r") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as file:
        json.dump(accounts, file)


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Foodlify")
        self.root.geometry("800x700")
        self.current_user = None
        self.email = None

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.accounts = load_accounts()
        self.current_frame = None

        self.show_login()

    def get_next_id(self):
        if not self.accounts:
            return 1
        existing_ids = [user["id"] for user in self.accounts.values()]
        return max(existing_ids) + 1

    def switch_frame(self, new_frame):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = new_frame
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_login(self):
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Login", font=("Arial", 24)).pack(pady=20)

        tk.Label(frame, text="Email:").pack(pady=5)
        email_entry = tk.Entry(frame, width=30)
        email_entry.pack()

        tk.Label(frame, text="Password:").pack(pady=5)
        password_entry = tk.Entry(frame, show="*", width=30)
        password_entry.pack()

        def login():
            email = email_entry.get().strip()
            password = password_entry.get().strip()

            if email in self.accounts and self.accounts[email]["password"] == password:
                self.current_user = {"id": self.accounts[email]["id"],"name": self.accounts[email]["name"],"password": self.accounts[email]["password"], "recipes": self.accounts[email]["recipes"]}
                self.email = email
                messagebox.showinfo("Success", "Login successful!")
                self.show_main_menu()
            else:
                messagebox.showerror("Error", "Invalid email or password.")

        tk.Button(frame, text="Login", command=login).pack(pady=20)
        tk.Button(frame, text="Register", command=self.show_register).pack(pady=10)

        self.switch_frame(frame)

    def show_register(self):
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Register", font=("Arial", 24)).pack(pady=20)

        tk.Label(frame, text="Name:").pack(pady=5)
        name_entry = tk.Entry(frame, width=30)
        name_entry.pack()

        tk.Label(frame, text="Email:").pack(pady=5)
        email_entry = tk.Entry(frame, width=30)
        email_entry.pack()

        tk.Label(frame, text="Password:").pack(pady=5)
        password_entry = tk.Entry(frame, show="*", width=30)
        password_entry.pack()

        def register():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get().strip()

            if not name or not email or not password:
                messagebox.showerror("Error", "All fields are required!")
                return

            if not validate_email(email):
                messagebox.showerror("Error", "Invalid email format!")
                return

            if email in self.accounts:
                messagebox.showerror("Error", "An account with this email already exists.")
                return

            user_id = self.get_next_id()
            self.accounts[email] = {"id": user_id, "name": name, "password": password, "recipes": []}
            save_accounts(self.accounts)
            messagebox.showinfo("Success", f"Account created successfully! Your ID is {user_id}")
            self.show_login()

        tk.Button(frame, text="Register", command=register).pack(pady=20)
        tk.Button(frame, text="Back to Login", command=self.show_login).pack(pady=10)

        self.switch_frame(frame)

    def show_main_menu(self):
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=0, sticky="nsew")

        tk.Label(frame, text="Main Menu", font=("Arial", 24)).pack(pady=20)

        tk.Button(frame, text="Profile Details", command=lambda: self.show_profile()).pack(pady=10)
        tk.Button(frame, text="View My Recipes", command=self.show_my_recipes).pack(pady=10)
        tk.Button(frame, text="Add a Recipe", command=lambda: self.show_add_recipe()).pack(pady=10)
        tk.Button(frame, text="Search", command=lambda: self.search()).pack(pady=10)
        tk.Button(frame, text="Search By Ingredients/Tags", command=lambda: self.special_search()).pack(pady=10)
        tk.Button(frame, text="Nearby Shops", command = self.shops_near_me).pack(pady=10)
        tk.Button(frame, text="Log Out", command=self.show_login).pack(pady=10)

        self.switch_frame(frame)

    def show_add_recipe(self):
        if self.current_user:
            menu_app = MenuApp(self, self.accounts, self.current_user,self.email)
            self.switch_frame(menu_app.get_frame())
        else:
            messagebox.showerror("Error", "No user logged in!")

    def show_profile(self):
        if self.current_user:
            menu_app = MenuApp(self, self.accounts, self.current_user, self.email)
            menu_app.view_profile_details()
        else:
            messagebox.showerror("Error", "No user logged in!")

    def show_my_recipes(self):
        menu_app = MenuApp(self, self.accounts, self.current_user, self.email)
        menu_app.show_my_recipes()

    def search(self):
        if self.current_user:
            menu_app = MenuApp(self, self.accounts, self.current_user, self.email)
            menu_app.search_recipes_page()
        else:
            messagebox.showerror("Error", "No user logged in!")


    def special_search(self):
        if self.current_user:
            menu_app = MenuApp(self, self.accounts, self.current_user, self.email)
            menu_app.special_search()
        else:
            messagebox.showerror("Error", "No user logged in!")


    def shops_near_me(self):
        url = "https://www.google.com/maps/search/supermarket/"
        webbrowser.open(url)


