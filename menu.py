import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
from PIL import Image, ImageTk
from functools import partial
import requests
from PIL import Image
from io import BytesIO



RECIPES_FILE = "recipes.json"
INGREDIENTS_FILE = "ingredients.json"
TAGS_FILE = "tags.json"


def load_data(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f)


def load_recipes():
    try:
        with open("recipes.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("recipes.json file not found. Starting with an empty recipe list.")
        return []
    except json.JSONDecodeError:
        print("Error decoding recipes.json. Starting with an empty recipe list.")
        return []


class MenuApp:
    def __init__(self, app_instance, accounts, current_user,email):
        self.app_instance = app_instance
        self.accounts = accounts
        self.current_user = current_user
        self.email = email
        self.ingredients = []
        self.tags = []
        self.frame = tk.Frame(self.app_instance.root)
        self.root = self.app_instance.root
        self.recipes = load_recipes()

        self.app_instance.root.geometry("800x700")

        self.root_frame = tk.Frame(self.app_instance.root)
        self.root_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.root_frame)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(self.root_frame, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")


        self.canvas.grid(row=0, column=0, sticky="ns")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.root_frame.rowconfigure(0, weight=1)
        self.root_frame.columnconfigure(0, weight=1)

        self.setup_ui()

    def get_frame(self):
        return self.frame

    def update_user(self):
        try:
            with open("accounts.json", "r") as f:
                accounts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            accounts = {}

        email = self.email
        if email in accounts:
            accounts[email] = self.current_user

            with open("accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)
        else:
            print("User not found in accounts.")

    def setup_ui(self):

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)


        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))


        title_label = tk.Label(self.scrollable_frame, text="Add a Recipe", font=("Arial", 24))
        title_label.pack(pady=(20, 10), anchor="center")

        name_label = tk.Label(self.scrollable_frame, text="Recipe Name:")
        name_label.pack(pady=(10, 5), anchor="center")
        self.recipe_name_entry = tk.Entry(self.scrollable_frame, width=50)
        self.recipe_name_entry.pack(anchor="center")

        image_label = tk.Label(self.scrollable_frame, text="Upload an Image:")
        image_label.pack(pady=(20, 5), anchor="center")
        image_button = tk.Button(self.scrollable_frame, text="Choose File", command=self.upload_image)
        image_button.pack(anchor="center")

        youtube_label = tk.Label(self.scrollable_frame, text="YouTube Tutorial Link:")
        youtube_label.pack(pady=(20, 5), anchor="center")
        self.youtube_link_entry = tk.Entry(self.scrollable_frame, width=50)
        self.youtube_link_entry.pack(anchor="center")

        ingredients_label = tk.Label(self.scrollable_frame, text="Ingredients:")
        ingredients_label.pack(pady=(20, 5), anchor="center")
        self.ingredients_frame = tk.Frame(self.scrollable_frame)
        self.ingredients_frame.pack(pady=5, anchor="center")
        self.add_ingredient_row()
        self.add_ingredient_button = tk.Button(self.scrollable_frame, text="Add Ingredient",
                                               command=self.add_ingredient_row)
        self.add_ingredient_button.pack(pady=10, anchor="center")

        instructions_label = tk.Label(self.scrollable_frame, text="Instructions:")
        instructions_label.pack(pady=(20, 5), anchor="center")
        self.instructions_text = tk.Text(self.scrollable_frame, height=10, width=50)
        self.instructions_text.pack(anchor="center")

        tags_label = tk.Label(self.scrollable_frame, text="Tags:")
        tags_label.pack(pady=(20, 5), anchor="center")
        self.tags_frame = tk.Frame(self.scrollable_frame)
        self.tags_frame.pack(pady=5, anchor="center")
        self.add_tag_row()
        self.add_tag_button = tk.Button(self.scrollable_frame, text="Add Tag", command=self.add_tag_row)
        self.add_tag_button.pack(pady=10, anchor="center")

        button_frame = tk.Frame(self.scrollable_frame)
        button_frame.pack(pady=20, anchor="center")
        tk.Button(button_frame, text="Back", command=self.go_back).pack(side="left", padx=20)
        tk.Button(button_frame, text="Submit", command=self.submit_recipe).pack(side="left", padx=20)

        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


    def upload_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if filepath:
            self.image_path = filepath
            messagebox.showinfo("Image Upload", "Image uploaded successfully!")

    def add_ingredient_row(self):
        if self.ingredients and (
            not self.ingredients[-1]["name"].get().strip() or not self.ingredients[-1]["quantity"].get().strip()
        ):
            messagebox.showwarning("Warning", "Please fill in the current ingredient before adding a new one.")
            return

        row = tk.Frame(self.ingredients_frame)
        row.pack(pady=5)

        ingredient_name = tk.Entry(row, width=30)
        ingredient_name.pack(side=tk.LEFT, padx=5)
        quantity = tk.Entry(row, width=10)
        quantity.pack(side=tk.LEFT, padx=5)

        self.ingredients.append({"name": ingredient_name, "quantity": quantity})

    def add_tag_row(self):
        if self.tags and not self.tags[-1].get().strip():
            messagebox.showwarning("Warning", "Please fill in the current tag before adding a new one.")
            return

        row = tk.Frame(self.tags_frame)
        row.pack(pady=5, anchor="w")

        tag_name = tk.Entry(row, width=40)
        tag_name.pack(side=tk.LEFT, padx=5)

        self.tags.append(tag_name)

    def submit_recipe(self):
        name = self.recipe_name_entry.get().strip()
        youtube_link = self.youtube_link_entry.get().strip()
        instructions = self.instructions_text.get("1.0", tk.END).strip()
        author_id = self.current_user["id"]
        username = self.current_user["name"]

        if not name or not instructions:
            messagebox.showerror("Error", "Recipe name and instructions are required!")
            return

        ingredients = []
        for entry in self.ingredients:
            ingredient_name = entry["name"].get().strip()
            quantity = entry["quantity"].get().strip()
            if ingredient_name and quantity:
                ingredients.append({"name": ingredient_name, "quantity": quantity})

        if not ingredients:
            messagebox.showerror("Error", "At least one ingredient is required!")
            return

        tags = [entry.get().strip() for entry in self.tags if entry.get().strip()]

        recipes = load_data(RECIPES_FILE)
        recipe = {
            "author_id": author_id,
            "username": username,
            "name": name,
            "image_path": getattr(self, "image_path", None),
            "youtube_link": youtube_link,
            "ingredients": ingredients,
            "instructions": instructions,
            "tags": tags,
        }
        recipes.append(recipe)
        save_data(RECIPES_FILE, recipes)

        ingredient_data = load_data(INGREDIENTS_FILE)
        ingredient_data.extend([ing["name"] for ing in ingredients if ing["name"] not in ingredient_data])
        save_data(INGREDIENTS_FILE, ingredient_data)

        tags_data = load_data(TAGS_FILE)
        tags_data.extend([tag for tag in tags if tag not in tags_data])
        save_data(TAGS_FILE, tags_data)

        self.current_user["recipes"].append(name)
        self.update_user()

        messagebox.showinfo("Success", "Recipe added successfully!")
        self.go_back()

    def go_back(self):
        self.app_instance.show_main_menu()

    def view_profile_details(self):
        for widget in self.app_instance.root.winfo_children():
            widget.destroy()

        profile_details_frame = tk.Frame(self.app_instance.root)
        profile_details_frame.grid(row=0, column=0, sticky="ns")

        title_label = tk.Label(profile_details_frame, text="Profile Details", font=("Arial", 24))
        title_label.grid(row=0, column=0, pady=20)

        details = [
            f"ID: {self.current_user.get('id', 'N/A')}",
            f"Name: {self.current_user.get('name', 'N/A')}",
            f"Email: {self.email}",
            f"Password: {self.accounts[self.email]['password']}",
            f"Number of Recipes: {len(self.current_user.get('recipes', []))}"
        ]

        for idx, detail in enumerate(details, start=1):
            detail_label = tk.Label(profile_details_frame, text=detail, font=("Arial", 14))
            detail_label.grid(row=idx, column=0, pady=5)

        back_button = tk.Button(profile_details_frame, text="Back", command=self.go_back)
        back_button.grid(row=len(details) + 1, column=0, pady=20)

        self.app_instance.root.update_idletasks()

    def show_my_recipes(self):
        recipes = load_data(RECIPES_FILE)
        user_recipes = [recipe for recipe in recipes if recipe["author_id"] == self.current_user["id"]]

        for widget in self.root.winfo_children():
            widget.destroy()

        if not user_recipes:
            messagebox.showinfo("No Recipes", "You don't have any recipes yet!")
            self.go_back()



        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="ns")
        scrollbar.grid(row=0, column=1, sticky="ns")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        center_frame = tk.Frame(scrollable_frame)
        center_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        scrollable_frame.grid_rowconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(0, weight=1)

        for idx, recipe in enumerate(user_recipes):
            recipe_button = tk.Button(
                center_frame,
                text=recipe["name"],
                font=("Arial", 14),
                command=lambda r=recipe: self.view_recipe_details(r)
            )
            recipe_button.grid(row=idx, column=0, pady=5,padx=140, sticky="ns")


        back_button = tk.Button(scrollable_frame, text="Back", command=self.go_back_to_main_menu)
        back_button.grid(row=len(user_recipes), column=0, pady=20, sticky="s")

    def view_recipe_details(self, recipe):
        for widget in self.root.winfo_children():
            widget.destroy()


        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        tk.Label(scrollable_frame, text=recipe["name"], font=("Arial", 24)).grid(row=0, column=0, pady=20, padx=150)

        tk.Label(scrollable_frame, text=f"By: {recipe['username']}", font=("Arial", 14)).grid(row=1, column=0, pady=10,
                                                                                               padx=20)

        if recipe.get("image_path"):
            try:
                if recipe["image_path"].startswith("http"):
                    response = requests.get(recipe["image_path"])
                    response.raise_for_status()
                    img_data = BytesIO(response.content)
                    img = Image.open(img_data)
                else:
                    img = Image.open(recipe["image_path"])

                img.thumbnail((400, 300))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(scrollable_frame, image=photo)
                img_label.image = photo
                img_label.grid(row=2, column=0, pady=10)
            except Exception as e:
                tk.Label(scrollable_frame, text="Image could not be loaded").grid(row=2, column=0, pady=10)

        if recipe.get("youtube_link"):
            yt_button = tk.Button(
                scrollable_frame,
                text="Watch Tutorial",
                command=lambda: os.system(f"start {recipe['youtube_link']}")
            )
            yt_button.grid(row=3, column=0, pady=10, padx=20)

        tk.Label(scrollable_frame, text="Ingredients", font=("Arial", 18)).grid(row=4, column=0, pady=10, padx=20)
        row = 5
        for ingredient in recipe["ingredients"]:
            ingredient_label = tk.Label(scrollable_frame, text=f"{ingredient['name']}: {ingredient['quantity']}")
            ingredient_label.grid(row=row, column=0, pady=2, padx=20, sticky="w")
            row += 1

        tk.Label(scrollable_frame, text="Instructions", font=("Arial", 18)).grid(row=row, column=0, pady=10, padx=20)
        row += 1
        tk.Label(scrollable_frame, text=recipe["instructions"], wraplength=600, justify="left").grid(row=row, column=0,
                                                                                                     pady=10, padx=20)
        row += 1

        if recipe.get("tags"):
            tk.Label(scrollable_frame, text="Tags", font=("Arial", 18)).grid(row=row, column=0, pady=10, padx=20)
            tags_text = ", ".join(recipe["tags"])
            tk.Label(scrollable_frame, text=tags_text).grid(row=row + 1, column=0, pady=5, padx=20)

        back_button = tk.Button(scrollable_frame, text="Back", command=self.go_back)
        back_button.grid(row=row + 2, column=0, pady=20, padx=20, sticky="s")

    def resize_image(self, image):
        max_size = (250, 250)
        image.thumbnail(max_size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

    def open_youtube(self, link):
        import webbrowser
        webbrowser.open(link)

    def switch_frame(self, new_frame):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = new_frame
        self.current_frame.pack(fill="both", expand=True)

    def go_back_to_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.app_instance.show_main_menu()

    def search_recipes_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky="ns")

        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        search_frame = tk.Frame(container)
        search_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.grid(row=0, column=0, padx=5)

        search_button = tk.Button(
            search_frame,
            text="Search",
            command=lambda: self.update_search_results(search_var.get())
        )
        search_button.grid(row=0, column=1, padx=5)

        results_frame = tk.Frame(container)
        results_frame.grid(row=1, column=0, sticky="nsew")

        self.canvas = tk.Canvas(results_frame)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.grid(row=0, column=0, sticky="ns")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        back_button = tk.Button(
            container,
            text="Back",
            command=self.app_instance.show_main_menu
        )
        back_button.grid(row=2, column=0, pady=10)

        self.update_search_results("")

    def search_recipes(self, query):
        query = query.strip().lower()
        results = []

        for recipe in self.recipes:
            name = recipe.get("name", "").lower()
            tags = recipe.get("tags", [])
            ingredients = recipe.get("ingredients", [])

            if query in name or any(query in tag.lower() for tag in tags) or any(
                    query in ing["name"].lower() for ing in ingredients):
                results.append(recipe)

        return results

    def update_search_results(self, query):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        search_results = self.search_recipes(query)
        for recipe in search_results:
            recipe_button = tk.Button(
                self.scrollable_frame,
                text=f"{recipe['name']}",
                anchor="w",
                command=lambda r=recipe: self.view_recipe_details(r)
            )
            recipe_button.pack(fill="x", pady=5, anchor="w")

        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def special_search(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky="ns")


        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        filter_button = tk.Button(
            container,
            text="Filter",
            command=self.open_filter_window
        )
        filter_button.grid(row=0, column=0, pady=10)


        results_frame = tk.Frame(container)
        results_frame.grid(row=1, column=0, sticky="nsew")


        self.canvas = tk.Canvas(results_frame)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.canvas.yview)


        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.grid(row=0, column=0, sticky="ns")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        back_button = tk.Button(
            container,
            text="Back",
            command=self.app_instance.show_main_menu
        )
        back_button.grid(row=2, column=0, pady=10)

        self.update_special_search_results([], [])

    def open_filter_window(self):
        filter_window = tk.Toplevel(self.root)
        filter_window.title("Filter Recipes")
        filter_window.geometry("400x600")

        container = tk.Frame(filter_window)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ingredients = load_data(INGREDIENTS_FILE)
        tags = load_data(TAGS_FILE)

        if not hasattr(self, "selected_ingredients"):
            self.selected_ingredients = []
        if not hasattr(self, "selected_tags"):
            self.selected_tags = []

        tk.Label(scrollable_frame, text="Ingredients", font=("Arial", 12, "bold")).pack(pady=5, anchor="w")

        ingredient_search_var = tk.StringVar()
        tk.Entry(
            scrollable_frame,
            textvariable=ingredient_search_var,
            font=("Arial", 10)
        ).pack(fill="x", padx=5, pady=5)

        ingredient_vars = {ing: tk.BooleanVar(value=(ing in self.selected_ingredients)) for ing in ingredients}
        ingredient_frame = tk.Frame(scrollable_frame)
        ingredient_frame.pack(fill="x", padx=5, pady=5)

        def update_ingredient_list(*args):
            for widget in ingredient_frame.winfo_children():
                widget.destroy()
            filtered_ingredients = [ing for ing in ingredients if ingredient_search_var.get().lower() in ing.lower()]
            for ingredient in filtered_ingredients:
                var = ingredient_vars[ingredient]
                tk.Checkbutton(ingredient_frame, text=ingredient, variable=var).pack(anchor="w")

        ingredient_search_var.trace("w", update_ingredient_list)
        update_ingredient_list()

        tk.Label(scrollable_frame, text="Tags", font=("Arial", 12, "bold")).pack(pady=10, anchor="w")

        tag_search_var = tk.StringVar()
        tk.Entry(
            scrollable_frame,
            textvariable=tag_search_var,
            font=("Arial", 10)
        ).pack(fill="x", padx=5, pady=5)

        tag_vars = {tag: tk.BooleanVar(value=(tag in self.selected_tags)) for tag in tags}
        tag_frame = tk.Frame(scrollable_frame)
        tag_frame.pack(fill="x", padx=5, pady=5)

        def update_tag_list(*args):
            for widget in tag_frame.winfo_children():
                widget.destroy()
            filtered_tags = [tag for tag in tags if tag_search_var.get().lower() in tag.lower()]
            for tag in filtered_tags:
                var = tag_vars[tag]
                tk.Checkbutton(tag_frame, text=tag, variable=var).pack(anchor="w")

        tag_search_var.trace("w", update_tag_list)
        update_tag_list()

        def apply_filters():
            self.selected_ingredients = [ing for ing, var in ingredient_vars.items() if var.get()]
            self.selected_tags = [tag for tag, var in tag_vars.items() if var.get()]
            filter_window.destroy()
            self.update_special_search_results(self.selected_ingredients, self.selected_tags)

        def clear_filters():
            self.selected_ingredients.clear()
            self.selected_tags.clear()
            for var in ingredient_vars.values():
                var.set(False)
            for var in tag_vars.values():
                var.set(False)
            update_ingredient_list()
            update_tag_list()

        tk.Button(filter_window, text="Apply Filters", command=apply_filters).pack(pady=10)
        tk.Button(filter_window, text="Clear Filters", command=clear_filters).pack(pady=10)

    def update_special_search_results(self, ingredients, tags):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not ingredients and not tags:
            filtered_recipes = self.recipes
        else:
            filtered_recipes = [
                recipe for recipe in self.recipes
                if all(
                    ing.lower() in [i["name"].lower() for i in recipe["ingredients"]]
                    for ing in ingredients
                ) and all(
                    tag.lower() in [t.lower() for t in recipe.get("tags", [])]
                    for tag in tags
                )
            ]

        if filtered_recipes:
            for recipe in filtered_recipes:
                recipe_button = tk.Button(
                    self.scrollable_frame,
                    text=f"{recipe['name']}",
                    anchor="w",
                    command=lambda r=recipe: self.view_recipe_details(r)
                )
                recipe_button.pack(fill="x", pady=5, anchor="w")
        else:
            tk.Label(
                self.scrollable_frame,
                text="No recipes found based on your filters.",
                font=("Arial", 12)
            ).pack(pady=10)

        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))






