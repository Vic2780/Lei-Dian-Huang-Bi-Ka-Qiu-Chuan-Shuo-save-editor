import csv
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ------------------------------------------------------------
# config
# ------------------------------------------------------------

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

SPECIES_INDEX_FILE = os.path.join(SCRIPT_DIRECTORY, "speciesIndex.txt")
MOVE_INDEX_FILE = os.path.join(SCRIPT_DIRECTORY, "moveIndex.txt")


# first party Pokémon offsets
SPECIES_ADDRESS = 0x0C33
LEVEL_ADDRESS = 0x0C39

MOVE_ADDRESSES = {
    1: 0x0C63,
    2: 0x0C69,
    3: 0x0C6F,
    4: 0x0C75,
}


# ------------------------------------------------------------
# load indexes from dictionary
# ------------------------------------------------------------

def load_species_index():
    species = {}

    with open(SPECIES_INDEX_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        for line_number, row in enumerate(reader, start=1):
            if not row:
                continue

            if len(row) < 2:
                raise ValueError(
                    f"{SPECIES_INDEX_FILE}\n"
                    f"Line {line_number} is missing the species name."
                )

            try:
                species_id = int(row[0].strip())
            except ValueError:
                raise ValueError(
                    f"{SPECIES_INDEX_FILE}\n"
                    f"Line {line_number} has an invalid species ID: "
                    f"{row[0]!r}"
                )

            species_name = row[1].strip()

            species[species_id] = species_name

    return species


def load_move_index():
    moves = {}

    with open(MOVE_INDEX_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        for line_number, row in enumerate(reader, start=1):
            if not row:
                continue

            if len(row) < 2:
                raise ValueError(
                    f"{MOVE_INDEX_FILE}\n"
                    f"Line {line_number} is missing the move name."
                )

            try:
                move_id = int(row[0].strip(), 16)
            except ValueError:
                raise ValueError(
                    f"{MOVE_INDEX_FILE}\n"
                    f"Line {line_number} has an invalid move ID: "
                    f"{row[0]!r}"
                )

            move_name = row[1].strip()

            moves[move_id] = move_name

    return moves


# ------------------------------------------------------------
# save checksum
# ------------------------------------------------------------

def calculate_checksum(data):
    checksum = 0
    c = 0

    for i in range(0x0C00, 0x1600):
        checksum = checksum + data[i] + c
        c = 0

        if checksum > 255:
            checksum = checksum & 255
            c = 1

    for i in range(0x1C00, 0x1C10):
        checksum = checksum + data[i]
        c = 0

        if checksum > 255:
            checksum = checksum & 255
            c = 1

    return checksum & 255


# ------------------------------------------------------------
# save editor
# ------------------------------------------------------------

class SaveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("雷电皇 比卡丘传说 SE")
        self.root.geometry("300x330")
        self.root.resizable(False, False)

        self.species = {}
        self.moves = {}

        self.save_data = None
        self.save_path = None

        self.species_by_name = {}
        self.moves_by_name = {}

        self.species_var = tk.StringVar()
        self.level_var = tk.StringVar()

        self.move_vars = {
            1: tk.StringVar(),
            2: tk.StringVar(),
            3: tk.StringVar(),
            4: tk.StringVar(),
        }

        self.status_var = tk.StringVar(value="No save loaded.")

        self.load_indexes()
        self.create_widgets()

    # --------------------------------------------------------
    # load index
    # --------------------------------------------------------

    def load_indexes(self):
        try:
            self.species = load_species_index()
            self.moves = load_move_index()

        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Index Error",
                str(error)
            )
            self.root.destroy()
            return

        self.species_by_name = {
            name: species_id
            for species_id, name in self.species.items()
        }

        self.moves_by_name = {
            name: move_id
            for move_id, name in self.moves.items()
        }

    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=15)
        main.grid(row=0, column=0, sticky="nsew")

        # open Save button
        open_button = ttk.Button(
            main,
            text="Open Save",
            command=self.open_save
        )
        open_button.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 15)
        )

        # species
        ttk.Label(
            main,
            text="Species:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 10),
            pady=4
        )

        self.species_dropdown = ttk.Combobox(
            main,
            textvariable=self.species_var,
            values=sorted(self.species.values()),
            state="readonly",
            width=30
        )
        self.species_dropdown.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=4
        )

        # level
        ttk.Label(
            main,
            text="Level:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=(0, 10),
            pady=4
        )

        self.level_entry = ttk.Entry(
            main,
            textvariable=self.level_var,
            width=10
        )
        self.level_entry.grid(
            row=2,
            column=1,
            sticky="w",
            pady=4
        )

        # moves
        self.move_dropdowns = {}

        for move_number in range(1, 5):
            ttk.Label(
                main,
                text=f"Move {move_number}:"
            ).grid(
                row=2 + move_number,
                column=0,
                sticky="w",
                padx=(0, 10),
                pady=4
            )

            dropdown = ttk.Combobox(
                main,
                textvariable=self.move_vars[move_number],
                values=sorted(self.moves.values()),
                state="readonly",
                width=30
            )

            dropdown.grid(
                row=2 + move_number,
                column=1,
                sticky="ew",
                pady=4
            )

            self.move_dropdowns[move_number] = dropdown

        # Save As
        save_button = ttk.Button(
            main,
            text="Save As...",
            command=self.save_as
        )
        save_button.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(15, 5)
        )

        # status message
        status_label = ttk.Label(
            main,
            textvariable=self.status_var,
            anchor="center"
        )
        status_label.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(5, 0)
        )

    # --------------------------------------------------------
    # open save
    # --------------------------------------------------------

    def open_save(self):
        file_path = filedialog.askopenfilename(
            title="Open Save File",
            filetypes=[
                ("Save files", "*.sav"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            with open(file_path, "rb") as file:
                data = bytearray(file.read())

        except OSError as error:
            messagebox.showerror(
                "Open Error",
                f"Could not open the save file:\n\n{error}"
            )
            return

        # make sure file is large enough for all offsets used
        required_size = 0x1C21

        if len(data) < required_size:
            messagebox.showerror(
                "Invalid Save",
                f"The selected file is too small.\n\n"
                f"Expected at least {required_size:#x} bytes, "
                f"but found {len(data):#x} bytes."
            )
            return

        self.save_data = data
        self.save_path = file_path

        self.update_fields_from_save()

        filename = os.path.basename(file_path)

        self.status_var.set(
            f"Loaded: {filename}"
        )

    # --------------------------------------------------------
    # read existing values from save
    # --------------------------------------------------------

    def update_fields_from_save(self):
        species_id = self.save_data[SPECIES_ADDRESS]
        level = self.save_data[LEVEL_ADDRESS]

        # species
        species_name = self.species.get(species_id)

        if species_name is None:
            species_name = f"Unknown ({species_id})"

        self.species_var.set(species_name)

        # level
        self.level_var.set(str(level))

        # moves
        for move_number, address in MOVE_ADDRESSES.items():
            move_id = self.save_data[address]
            move_name = self.moves.get(move_id)

            if move_name is None:
                move_name = f"Unknown (0x{move_id:02X})"

            self.move_vars[move_number].set(move_name)

    # --------------------------------------------------------
    # Save As
    # --------------------------------------------------------

    def save_as(self):
        if self.save_data is None:
            messagebox.showwarning(
                "No Save Loaded",
                "Open a save file before saving."
            )
            return

        try:
            self.update_save_data()

        except ValueError as error:
            messagebox.showerror(
                "Invalid Value",
                str(error)
            )
            return

        original_name = os.path.basename(self.save_path)

        output_path = filedialog.asksaveasfilename(
            title="Save Edited File",
            initialfile=original_name,
            defaultextension=".sav",
            filetypes=[
                ("Save files", "*.sav"),
                ("All files", "*.*")
            ]
        )

        if not output_path:
            return

        try:
            with open(output_path, "wb") as file:
                file.write(self.save_data)

        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Could not save the file:\n\n{error}"
            )
            return

        self.status_var.set(
            f"Saved: {os.path.basename(output_path)}"
        )

        messagebox.showinfo(
            "Save Complete",
            f"Save file written successfully:\n\n{output_path}"
        )

    # --------------------------------------------------------
    # write GUI values to save
    # --------------------------------------------------------

    def update_save_data(self):
        # species
        species_name = self.species_var.get()

        if species_name not in self.species_by_name:
            raise ValueError(
                "Please select a valid species."
            )

        species_id = self.species_by_name[species_name]

        if not 1 <= species_id <= 159:
            raise ValueError(
                "Species ID must be between 1 and 159."
            )

        self.save_data[SPECIES_ADDRESS] = species_id

        # level
        level_text = self.level_var.get().strip()

        try:
            level = int(level_text)
        except ValueError:
            raise ValueError(
                "Level must be a whole number."
            )

        if not 1 <= level <= 100:
            raise ValueError(
                "Level must be between 1 and 100."
            )

        self.save_data[LEVEL_ADDRESS] = level

        # moves
        for move_number, address in MOVE_ADDRESSES.items():
            move_name = self.move_vars[move_number].get()

            if move_name not in self.moves_by_name:
                raise ValueError(
                    f"Please select a valid move for Move {move_number}."
                )

            move_id = self.moves_by_name[move_name]

            if not 0 <= move_id <= 0xFF:
                raise ValueError(
                    f"Move {move_number} has an invalid ID: "
                    f"0x{move_id:X}"
                )

            self.save_data[address] = move_id

        # recalculate checksum
        old_checksum = self.save_data[0x1C20]

        new_checksum = calculate_checksum(self.save_data)

        self.save_data[0x1C20] = new_checksum

        print(
            f"Checksum: "
            f"0x{old_checksum:02X} -> 0x{new_checksum:02X}"
        )


# ------------------------------------------------------------
# start program
# ------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditor(root)
    root.mainloop()