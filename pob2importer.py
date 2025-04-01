import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import os
import xml.etree.ElementTree as ET
import codeall  # Make sure codeall.py is in the same directory

# API URLs
CHARACTERS_URL = "https://planners.maxroll.gg/poe/characters?realm=poe2"
CHARACTER_DETAIL_URL = "https://planners.maxroll.gg/poe/character?realm=poe2&name="

PREFERENCES_FILE = "preferences.json"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Character Application")
        self.geometry("900x700")
        
        # Configuration frame
        config_frame = ttk.LabelFrame(self, text="Config")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # Frame for cookie and buttons
        cookie_frame = ttk.Frame(config_frame)
        cookie_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(cookie_frame, text="Cookie:").pack(side="left", padx=5, pady=5)
        
        # Entry for cookie (with password mode by default)
        self.cookie_entry = ttk.Entry(cookie_frame, width=40, show="*")
        self.cookie_entry.pack(side="left", padx=5, pady=5)
        
        # Variable to control cookie visibility
        self.show_cookie = tk.BooleanVar(value=False)
        
        # Button to show/hide cookie
        self.toggle_btn = ttk.Button(cookie_frame, text="Show", command=self.toggle_cookie_visibility)
        self.toggle_btn.pack(side="left", padx=5, pady=5)
        
        # Button to save cookie in preferences
        save_cookie_btn = ttk.Button(cookie_frame, text="Save Cookie", command=self.save_cookie)
        save_cookie_btn.pack(side="left", padx=5, pady=5)
        
        # Information button about how to get the cookie
        info_btn = ttk.Button(cookie_frame, text="Info", command=self.show_cookie_info)
        info_btn.pack(side="left", padx=5, pady=5)
        
        # Button to update characters
        update_btn = ttk.Button(self, text="Update", command=self.load_characters)
        update_btn.pack(pady=5)
        
        # Frame with scrollbar for character cards
        cards_container = ttk.Frame(self)
        cards_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar for cards frame
        scrollbar = ttk.Scrollbar(cards_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        # Canvas to allow scrolling
        self.canvas = tk.Canvas(cards_container, yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        
        # Frame inside canvas for cards
        self.cards_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        
        # Configure canvas to adjust internal frame size
        self.cards_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Frame to show details and PoB code
        details_frame = ttk.LabelFrame(self, text="Character Details")
        details_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Text box to show character JSON
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap="none", height=8)  # Reduced height
        self.details_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Button to process JSON manually
        process_btn = ttk.Button(details_frame, text="Process", command=self.process_json_from_text)
        process_btn.pack(pady=5)
        
        # Frame to show generated PoB code
        pob_frame = ttk.LabelFrame(self, text="PoB Code")
        pob_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Frame for text and copy button
        pob_content_frame = ttk.Frame(pob_frame)
        pob_content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Text box for PoB code
        self.pob_text = scrolledtext.ScrolledText(pob_content_frame, wrap="none", height=6)  # Reduced height
        self.pob_text.pack(side="left", fill="both", expand=True)
        
        # Button to copy PoB code
        copy_btn = ttk.Button(pob_content_frame, text="Copy", command=self.copy_pob_code)
        copy_btn.pack(side="right", padx=5, fill="y")
        
        # Load preferences (cookie) on startup
        self.load_preferences()
        # If cookie is already saved, load characters automatically
        if self.cookie_entry.get().strip():
            self.load_characters()
    
    def toggle_cookie_visibility(self):
        """Toggle between showing and hiding the cookie."""
        current_value = self.show_cookie.get()
        self.show_cookie.set(not current_value)
        
        if self.show_cookie.get():
            self.cookie_entry.config(show="")
            self.toggle_btn.config(text="Hide")
        else:
            self.cookie_entry.config(show="*")
            self.toggle_btn.config(text="Show")
    
    def on_frame_configure(self, event):
        """Update the canvas scrollable region."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Adjust the internal frame width to the canvas width."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def copy_pob_code(self):
        """Copy PoB code to clipboard."""
        pob_code = self.pob_text.get("1.0", tk.END).strip()
        if not pob_code:
            messagebox.showinfo("Info", "There is no PoB code to copy.")
            return
        
        # Clear clipboard and add the code
        self.clipboard_clear()
        self.clipboard_append(pob_code)
        
        messagebox.showinfo("Info", "PoB code copied to clipboard.")
    
    def load_preferences(self):
        """Load saved cookie from preferences file."""
        if os.path.exists(PREFERENCES_FILE):
            try:
                with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                    cookie = prefs.get("cookie", "")
                    self.cookie_entry.delete(0, tk.END)
                    self.cookie_entry.insert(0, cookie)
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not load configuration:\n{e}")
    
    def save_cookie(self):
        """Save the entered cookie to preferences file."""
        cookie = self.cookie_entry.get().strip()
        if not cookie:
            messagebox.showerror("Error", "You must enter a cookie before saving it.")
            return
        try:
            with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
                json.dump({"cookie": cookie}, f, indent=4)
            messagebox.showinfo("Info", "Cookie saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving cookie:\n{e}")
    
    def show_cookie_info(self):
        """Show information about how to get the cookie."""
        info = """How to obtain the Cookie:

1. You must register and have an account at https://maxroll.gg/

2. Go to https://maxroll.gg/poe2/planner and click the "Import from your PoE2 Account!" button. You may be asked to link your account with pathofexile, if so you must grant access.

3. Your character to import will appear. To obtain the Cookie, you should close the character selection box.

4. Open F12 Developer Tools and go to the "Network" tab. Filter by the URL: https://planners.maxroll.gg/poe/characters?realm=poe2

5. Go to the Headers section and scroll down until you find the entry that says "Cookie". That's the one you need to copy and paste into the Cookie field for the app to work properly."""
        
        # Create information window
        info_window = tk.Toplevel(self)
        info_window.title("Cookie Information")
        info_window.geometry("600x400")
        
        # Scrollable text box for information
        info_text = scrolledtext.ScrolledText(info_window, wrap="word")
        info_text.pack(fill="both", expand=True, padx=10, pady=10)
        info_text.insert("1.0", info)
        info_text.configure(state="disabled")  # Make text read-only
        
        # Button to close the window
        close_btn = ttk.Button(info_window, text="Close", command=info_window.destroy)
        close_btn.pack(pady=10)
    
    def load_characters(self):
        """Load character list, verifying cookie has been configured."""
        cookie = self.cookie_entry.get().strip()
        if not cookie:
            messagebox.showerror("Error", "You must enter and save the cookie before updating.")
            return
        
        headers = {"Cookie": cookie}
        try:
            response = requests.get(CHARACTERS_URL, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            messagebox.showerror("Error", f"Error getting characters:\n{e}")
            return
        
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        characters = data.get("characters", [])
        if not characters:
            ttk.Label(self.cards_frame, text="No characters found.").pack()
            return
        
        # Create a card for each character
        for char in characters:
            card = ttk.Frame(self.cards_frame, borderwidth=1, relief="solid", padding=10)
            card.pack(fill="x", pady=5)
            
            # Show main information
            info = (f"Name: {char.get('name')}\n"
                    f"Level: {char.get('level')}\n"
                    f"Class: {char.get('class')}\n"
                    f"League: {char.get('league')}")
            ttk.Label(card, text=info, justify="left").pack(side="left", padx=5)
            
            # Button to view character details
            btn = ttk.Button(card, text="View details", 
                             command=lambda name=char.get('name'): self.get_character_detail(name))
            btn.pack(side="right", padx=5)
        
        # Update scrollable region after adding cards
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def get_character_detail(self, name):
        """Query character details using cookie in header,
        displays JSON on screen and processes it to get PoB code."""
        cookie = self.cookie_entry.get().strip()
        if not cookie:
            messagebox.showerror("Error", "You must enter and save the cookie before querying details.")
            return
        
        headers = {"Cookie": cookie}
        url = CHARACTER_DETAIL_URL + name
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            detail_json = response.json()
        except Exception as e:
            messagebox.showerror("Error", f"Error getting character details:\n{e}")
            return
        
        # Save JSON to character.json file
        try:
            with open("character.json", "w", encoding="utf-8") as f:
                json.dump(detail_json, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving character.json file:\n{e}")
            return
        
        # Show JSON in text box
        self.details_text.delete("1.0", tk.END)
        formatted_json = json.dumps(detail_json, indent=4)
        self.details_text.insert(tk.END, formatted_json)
        
        # Automatically process JSON to get PoB code
        pob_code = self.process_character_json(detail_json)
        self.pob_text.delete("1.0", tk.END)
        self.pob_text.insert(tk.END, pob_code)
    
    def process_character_json(self, data):
        """Process character JSON using codeall.py functions
        to generate PoB code."""
        try:
            # Build XML from JSON
            root = codeall.build_xml_from_character(data)
            # (Optional) Indentation for better reading
            try:
                ET.indent(root, space="    ")
            except Exception:
                pass
            xml_bytes = ET.tostring(root, encoding="utf-8", method="xml")
            # Generate PoB code using codeall.py function
            pob_code = codeall.encode_to_pob(xml_bytes)
            return pob_code
        except Exception as e:
            messagebox.showerror("Error", f"Error processing JSON: {e}")
            return ""
    
    def process_json_from_text(self):
        """Process JSON from Character Details text box.
        Updates character.json file and displays PoB code."""
        json_text = self.details_text.get("1.0", tk.END).strip()
        if not json_text:
            messagebox.showerror("Error", "JSON text box is empty.")
            return
        try:
            data = json.loads(json_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing JSON:\n{e}")
            return
        
        # Update character.json file with modified JSON
        try:
            with open("character.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating character.json file:\n{e}")
            return
        
        # Process JSON to get PoB code
        pob_code = self.process_character_json(data)
        self.pob_text.delete("1.0", tk.END)
        self.pob_text.insert(tk.END, pob_code)
        messagebox.showinfo("Info", "JSON processed and file updated.")
        
if __name__ == "__main__":
    app = App()
    app.mainloop()