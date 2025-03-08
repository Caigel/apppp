import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import logging

API_URL = "http://127.0.0.1:5000/ingredients"

logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class UserInterface:
    def __init__(self, root):
        self.root = root
        self.tree = None  # Define Treeview as None initially
        self.user_name = self.get_user_name()
        self.setup_ui()

    def get_user_name(self):
        user_name = simpledialog.askstring("Input", "Enter your name:", parent=self.root)
        if not user_name:
            messagebox.showerror("Error", "Name is required to use the application.")
            self.root.destroy()
        return user_name

    def setup_ui(self):
        self.root.title("Subway Prepped Inventory Manager")
        self.root.geometry("600x400")
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        self.show_main_menu()

    def show_main_menu(self):
        self.clear_frame()
        tk.Button(self.container, text="Add Ingredient", command=self.open_add_ingredient).pack(pady=10)
        tk.Button(self.container, text="View Inventory", command=self.show_view_inventory).pack(pady=10)

    def open_add_ingredient(self):
        self.clear_frame()
        tk.Label(self.container, text="Ingredient Name:").pack(pady=5)
        self.name_entry = tk.Entry(self.container)
        self.name_entry.pack(pady=5)

        tk.Label(self.container, text="Current Amount:").pack(pady=5)
        self.current_amount_entry = tk.Entry(self.container)
        self.current_amount_entry.pack(pady=5)

        tk.Label(self.container, text="Target Amount:").pack(pady=5)
        self.target_amount_entry = tk.Entry(self.container)
        self.target_amount_entry.pack(pady=5)

        tk.Label(self.container, text="Waste Amount:").pack(pady=5)
        self.waste_amount_entry = tk.Entry(self.container)
        self.waste_amount_entry.pack(pady=5)

        tk.Button(self.container, text="Submit", command=self.submit_ingredient).pack(pady=10)
        tk.Button(self.container, text="Back", command=self.show_main_menu).pack(pady=10)

    def edit_selected_ingredient(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an ingredient to edit.")
            return
    
        # Get the selected ingredient's details
        values = self.tree.item(selected_item, 'values')
        ingredient_id = values[0]  # Assuming ID is the first column
    
    # Open a form for editing
        tk.Label(self.container, text="Edit Ingredient").pack(pady=5)
    
        tk.Label(self.container, text="Prepped Amount:").pack(pady=5)
        self.prepped_amount_entry = tk.Entry(self.container)
        self.prepped_amount_entry.pack(pady=5)


        tk.Button(self.container, text="Submit", command=self.submit_edit).pack(pady=5)
        tk.Button(self.container, text="Back", command=self.show_view_inventory).pack(pady=5)

    def submit_edit(self):
        try:
        # Get the selected ingredient ID from Treeview

            if not hasattr(self, 'tree') or not self.tree:
                messagebox.showerror("Error", "Inventory list is not available.")
                return


            selected_item = self.tree.selection()
            if not selected_item:
                 messagebox.showwarning("No selection", "Please select an ingredient to edit.")
                 return
        
            item = self.tree.item(selected_item)
            ingredient_id = item['values'][0]  # Assuming the ID is in the first column

        # Get the new prepped amount from the Entry widget
            new_prepped_amount_str = self.prepped_amount_entry.get()
            if not new_prepped_amount_str:
                messagebox.showwarning("Input Error", "Please enter a valid prepped amount.")
                return

            new_prepped_amount = int(new_prepped_amount_str)
            if new_prepped_amount < 0:
                raise ValueError("Prepped amount must be non-negative.")

        # Call the API to update the ingredient
            response = requests.put(f"{API_URL}/{ingredient_id}", json={"prepped_amount": new_prepped_amount})

        # Check if the request was successful
            if response.status_code == 200:
                logging.info(f"Ingredient updated: ID {ingredient_id} with new prepped amount: {new_prepped_amount}")
                messagebox.showinfo("Success", "Ingredient updated successfully.")
                self.show_view_inventory()  # Refresh the inventory
            else:
            # Log the response content for debugging
                logging.error(f"Error updating ingredient: {response.status_code} - {response.text}")
                messagebox.showerror("Error", f"Failed to update ingredient. Server response: {response.status_code}")
    
        except ValueError as ve:
            messagebox.showerror("Error", f"Invalid input: {ve}")
        except Exception as e:
            logging.error(f"Error updating ingredient: {e}")
            messagebox.showerror("Error", "Failed to update ingredient.")

    
        self.show_view_inventory()  # Refresh the inventory view


    def delete_selected_ingredient(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an ingredient to delete.")
            return

    # Get the selected ingredient's ID
        values = self.tree.item(selected_item, 'values')
        ingredient_id = values[0]  # Assuming ID is the first column
    
    # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this ingredient?"):
            return

        try:
        # Call API to delete
            response = requests.delete(f"{API_URL}/{ingredient_id}")
            if response.status_code == 200:
                logging.info(f"Ingredient deleted: ID {ingredient_id}")
                messagebox.showinfo("Success", "Ingredient deleted successfully.")
                self.show_view_inventory()  # Refresh the inventory
            else:
                raise Exception("Failed to delete ingredient.")
        except Exception as e:
            logging.error(f"Error deleting ingredient: {e}")
            messagebox.showerror("Error", "Failed to delete ingredient.")


    def submit_ingredient(self):
        try:
            prepped_amount = int(self.current_amount_entry.get() or 0)
            required_amount = int(self.target_amount_entry.get() or 0)
            waste_amount = int(self.waste_amount_entry.get() or 0)

            if prepped_amount < 0 or required_amount < 0 or waste_amount < 0:
                raise ValueError("Amounts must be non-negative.")

            data = {
                "name": self.name_entry.get(),
                "prepped_amount": prepped_amount,
                "required_amount": required_amount,
                "prepped_by": self.user_name,
                "waste_amount": waste_amount
            }
            response = requests.post(API_URL, json=data)
            if response.status_code == 201:
                logging.info(f"Ingredient added: {data}")
                messagebox.showinfo("Success", "Ingredient added successfully!")
            else:
                raise Exception("Failed to add ingredient o.")
        except ValueError as ve:
            logging.error(f"Input Error: {ve}")
            messagebox.showerror("Error", f"Invalid input: {ve}")
        except Exception as e:
            logging.error(f"Error in submit_ingredient: {e}")
            messagebox.showerror("Error", "Failed to add ingredient p.")
        self.show_main_menu()

    def show_view_inventory(self):
        self.clear_frame()
        
    # Now, create the Treeview for the inventory
        columns = ("ID", "Name", "Prepped Amount", "Required Amount", "Prepped By", "Waste Amount")
        self.tree = ttk.Treeview(self.container, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)  # Ensure it expands to take available space

        self.load_inventory()

        #tk.Button(self.container, text="Edit Selected", command=self.edit_selected_ingredient).pack(pady=5)
        tk.Button(self.container, text="Edit Selected", command=self.edit_selected_ingredient).pack(pady=5)
        tk.Button(self.container, text="Delete Selected", command=self.delete_selected_ingredient).pack(pady=5)
        tk.Button(self.container, text="Back", command=self.show_main_menu).pack(pady=10)


    def load_inventory(self):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                for item in response.json():
                    self.tree.insert("", "end", values=(item["id"], item["name"], item["prepped_amount"], item["required_amount"], item["prepped_by"], item["waste_amount"]))
            else:
                raise Exception("Failed to load inventory.")
        except Exception as e:
            logging.error(f"Error in load_inventory: {e}")
            messagebox.showerror("Error", "Failed to load inventory.")

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()
