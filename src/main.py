import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import os
import asyncio
from pathlib import Path

CONFIG_FILE = Path("config.json")

SYSTEMS = {
    "Atari - 2600": 25,
    "Atari - 7800": 51,
    "Atari - Jaguar": 17,
    "Atari - Jaguar CD": 77,
    "Atari - Lynx": 13,
    "Atari - 5200": 50,
    "Atari - ST": 36,
    "NEC - PC-8000/8800": 47,
    "NEC - PC Engine/TurboGrafx-16": 8,
    "NEC - PC Engine CD/TurboGrafx-CD": 76,
    "NEC - PC-FX": 49,
    "NEC - PC-6000": 67,
    "NEC - PC-9800": 48,
    "Nintendo - Nintendo Entertainment System": 7,
    "Nintendo - Famicom Disk System": 81,
    "Nintendo - Super Nintendo Entertainment System": 3,
    "Nintendo - Nintendo 64": 2,
    "Nintendo - GameCube": 16,
    "Nintendo - Wii": 19,
    "Nintendo - Game Boy": 4,
    "Nintendo - Game Boy Color": 6,
    "Nintendo - Game Boy Advance": 5,
    "Nintendo - Nintendo DS": 18,
    "Nintendo - Nintendo DSi": 78,
    "Nintendo - Pokemon Mini": 24,
    "Nintendo - Nintendo 3DS": 62,
    "Nintendo - Virtual Boy": 28,
    "Nintendo - Game & Watch": 60,
    "Nintendo - Wii U": 20,
    "Sega - SG-1000": 33,
    "Sega - Master System": 11,
    "Sega - Genesis/Mega Drive": 1,
    "Sega - Sega CD": 9,
    "Sega - 32X": 10,
    "Sega - Saturn": 39,
    "Sega - Dreamcast": 40,
    "Sega - Game Gear": 15,
    "Sega - Pico": 68,
    "SNK - Neo Geo CD": 56,
    "SNK - Neo Geo Pocket": 14,
    "Sony - PlayStation": 12,
    "Sony - PlayStation 2": 21,
    "Sony - PlayStation Portable": 41,
    "Others - 3DO Interactive Multiplayer": 43,
    "Others - Amstrad CPC": 37,
    "Others - Apple II": 38,
    "Others - Arcade": 27,
    "Others - Arcadia 2001": 73,
    "Others - Arduboy": 71,
    "Others - ColecoVision": 44,
    "Others - Elektor TV Games Computer": 75,
    "Others - Fairchild Channel F": 57,
    "Others - Intellivision": 45,
    "Others - Interton VC 4000": 74,
    "Others - Magnavox Odyssey 2": 23,
    "Others - Mega Duck": 69,
    "Others - MSX": 29,
    "Others - Uzebox": 80,
    "Others - Vectrex": 46,
    "Others - WASM-4": 72,
    "Others - Watara Supervision": 63,
    "Others - WonderSwan": 53
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RA Hash Checker")
        self.geometry("900x600")
        
        # Use native theme
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
            
        self.files_to_hash = []
        self.load_config()
        self.create_widgets()

    def load_config(self):
        self.config = {"username": "", "api_key": "", "hasher_path": ""}
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config.update(json.load(f))
            except Exception:
                pass

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top Config Section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Username
        ttk.Label(config_frame, text="Username:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.username_var = tk.StringVar(value=self.config["username"])
        self.username_var.trace_add("write", lambda *args: self.update_config("username", self.username_var.get()))
        ttk.Entry(config_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # API Key
        ttk.Label(config_frame, text="API Key:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.api_key_var = tk.StringVar(value=self.config["api_key"])
        self.api_key_var.trace_add("write", lambda *args: self.update_config("api_key", self.api_key_var.get()))
        ttk.Entry(config_frame, textvariable=self.api_key_var, width=40, show="*").grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Hasher Path
        ttk.Label(config_frame, text="RAHasher.exe:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.hasher_var = tk.StringVar(value=self.config["hasher_path"])
        ttk.Entry(config_frame, textvariable=self.hasher_var, state="readonly", width=30).grid(row=1, column=1, columnspan=2, sticky="we", padx=5, pady=2)
        ttk.Button(config_frame, text="Browse...", command=self.browse_hasher).grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        # System selection
        ttk.Label(config_frame, text="Console:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.system_var = tk.StringVar()
        self.system_combo = ttk.Combobox(config_frame, textvariable=self.system_var, values=list(SYSTEMS.keys()), state="readonly", width=40)
        self.system_combo.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=2)
        if list(SYSTEMS.keys()):
            self.system_combo.current(0)
            
        # Middle Section (Split pane)
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left pane: Files list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Add Files...", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_files).pack(side=tk.LEFT, padx=2)
        
        self.files_listbox = tk.Listbox(left_frame)
        self.files_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Right pane: Results
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        ttk.Button(right_frame, text="Hash Files", command=self.run_hashing).pack(fill=tk.X, pady=2)
        
        columns = ("file", "hash", "status", "game")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        self.tree.heading("file", text="File Name")
        self.tree.heading("hash", text="Hash")
        self.tree.heading("status", text="Match Status")
        self.tree.heading("game", text="Matched Game")
        
        self.tree.column("file", width=150)
        self.tree.column("hash", width=200)
        self.tree.column("status", width=120)
        self.tree.column("game", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bottom Status
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w").pack(fill=tk.X, pady=(5, 0))

    def update_config(self, key, value):
        self.config[key] = value
        self.save_config()

    def browse_hasher(self):
        path = filedialog.askopenfilename(title="Select RAHasher.exe", filetypes=[("Executable", "*.exe"), ("All Files", "*.*")])
        if path:
            self.hasher_var.set(path)
            self.update_config("hasher_path", path)

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select files to hash")
        if paths:
            for p in paths:
                if p not in self.files_to_hash:
                    self.files_to_hash.append(p)
                    self.files_listbox.insert(tk.END, os.path.basename(p))

    def clear_files(self):
        self.files_to_hash.clear()
        self.files_listbox.delete(0, tk.END)

    def run_hashing(self):
        if not self.config["hasher_path"]:
            messagebox.showerror("Error", "Please select RAHasher.exe location.")
            return
            
        if not self.files_to_hash:
            messagebox.showerror("Error", "Please add files to hash.")
            return
            
        system = self.system_var.get()
        if not system:
            return
            
        console_id = SYSTEMS[system]
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Run async task
        asyncio.run(self.process_files(console_id))

    async def process_files(self, console_id):
        results = []
        for idx, file_path in enumerate(self.files_to_hash):
            file_name = os.path.basename(file_path)
            self.status_var.set(f"Hashing {idx+1}/{len(self.files_to_hash)}: {file_name}")
            self.update()
            
            try:
                proc = subprocess.run([self.config["hasher_path"], str(console_id), file_path], 
                                      capture_output=True, text=True, check=True)
                output = proc.stdout.strip()
                # first token of first non-empty line
                first_line = next((line for line in output.split("\\n") if line.strip()), "")
                file_hash = first_line.split()[0] if first_line else ""
                
                # Verify hash length (32 hex characters)
                if len(file_hash) != 32 or not all(c in "0123456789abcdefABCDEF" for c in file_hash):
                    file_hash = "Invalid Hash"
            except Exception as e:
                file_hash = f"Error: {e}"
                
            results.append({"path": file_path, "name": file_name, "hash": file_hash})
            self.tree.insert("", tk.END, values=(file_name, file_hash, "Pending API Check...", ""))
            self.update()
            
        self.status_var.set("Fetching RetroAchievements Data...")
        self.update()
        
        try:
            # We would use the api-python package here.
            # Example using the retroachievements module:
            import retroachievements as ra
            
            # Since we don't know the exact API of the WIP library, we assume something like this based on typical usage:
            try:
                client = ra.RetroAchievements(username=self.config["username"], api_key=self.config["api_key"])
                games = client.get_game_list(console_id, hashes=True)
                
                hash_to_game = {}
                for g in games:
                    for h in getattr(g, "hashes", []):
                        hash_to_game[h] = g
                        
                # Update Treeview with results
                for idx, res in enumerate(results):
                    item_id = self.tree.get_children()[idx]
                    h = res["hash"]
                    if h in hash_to_game:
                        game = hash_to_game[h]
                        title = getattr(game, "title", "Unknown Game")
                        achievements = getattr(game, "num_achievements", 0)
                        status = "✓ Has achievements" if achievements > 0 else "Found, but no achievements"
                        self.tree.item(item_id, values=(res["name"], h, status, title))
                    elif h and len(h) == 32:
                        self.tree.item(item_id, values=(res["name"], h, "Not in RA", ""))
                    else:
                        self.tree.item(item_id, values=(res["name"], h, "Failed", ""))
                        
            except AttributeError:
                self.status_var.set("RA API package usage may differ from assumed implementation.")
                
        except Exception as e:
            self.status_var.set(f"RA API Check Failed: {e}")
            for idx, res in enumerate(results):
                item_id = self.tree.get_children()[idx]
                if self.tree.item(item_id)["values"][2] == "Pending API Check...":
                    self.tree.item(item_id, values=(res["name"], res["hash"], "API Error", ""))
        
        self.status_var.set("Ready.")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
