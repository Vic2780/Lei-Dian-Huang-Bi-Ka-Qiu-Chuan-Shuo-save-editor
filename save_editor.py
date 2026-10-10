import csv
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ------------------------------------------------------------
# config
# ------------------------------------------------------------

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

SPECIES_INDEX_FILE = os.path.join(
    SCRIPT_DIRECTORY, "speciesIndex.txt"
)
MOVE_INDEX_FILE = os.path.join(
    SCRIPT_DIRECTORY, "moveIndex.txt"
)

# base addresses for the first record
# each subsequent party Pokémon is shifted forward by one byte

SPECIES_ADDRESS = 0x0C33
LEVEL_ADDRESS = 0x0C39

MOVE_ADDRESSES = {
    1: 0x0C63,
    2: 0x0C69,
    3: 0x0C6F,
    4: 0x0C75,
}

POKEMON_SLOT_COUNT = 6


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
        self.root.geometry("380x500")
        self.root.resizable(False, False)

        self.species = {}
        self.moves = {}

        self.save_data = None
        self.save_path = None

        self.species_by_name = {}
        self.moves_by_name = {}

        # record slot currently displayed by the editor
        self.current_slot = None

        # prevent list refreshes from being treated as user selections
        self.refreshing_slots = False

        self.species_var = tk.StringVar()
        self.level_var = tk.StringVar()
        self.selected_var = tk.StringVar(
            value="No Pokémon selected."
        )

        self.move_vars = {
            1: tk.StringVar(),
            2: tk.StringVar(),
            3: tk.StringVar(),
            4: tk.StringVar(),
        }

        self.status_var = tk.StringVar(
            value="No save loaded."
        )

        self.load_indexes()
        self.create_widgets()

    # --------------------------------------------------------
    # load indexes
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
    # calculate addresses for a party slot
    # --------------------------------------------------------

    def get_species_address(self, slot):
        return SPECIES_ADDRESS + slot - 1

    def get_level_address(self, slot):
        return LEVEL_ADDRESS + slot - 1

    def get_move_addresses(self, slot):
        offset = slot - 1

        return {
            move_number: address + offset
            for move_number, address in MOVE_ADDRESSES.items()
        }

    def get_party_count(self):
        if self.save_data is None:
            return 0

        return min(
            self.save_data[PARTY_COUNT_ADDRESS],
            MAX_PARTY_SIZE
        )

    # --------------------------------------------------------
    # GUI
    # --------------------------------------------------------

    def create_widgets(self):
        main = ttk.Frame(self.root, padding=15)
        main.grid(row=0, column=0, sticky="nsew")

        main.columnconfigure(1, weight=1)

        # Open Save
        ttk.Button(
            main,
            text="Open Save",
            command=self.open_save
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 12)
        )

        # party Pokémon list
        ttk.Label(
            main,
            text="Select Pokémon record to edit"
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 5)
        )

        list_frame = ttk.Frame(main)
        list_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 10)
        )

        list_frame.columnconfigure(0, weight=1)

        self.slot_list = tk.Listbox(
            list_frame,
            height=POKEMON_SLOT_COUNT,
            width=38,
            exportselection=False,
            selectmode=tk.SINGLE,
            activestyle="dotbox"
        )

        self.slot_list.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        slot_scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.slot_list.yview
        )

        slot_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.slot_list.configure(
            yscrollcommand=slot_scrollbar.set
        )

        self.slot_list.bind(
            "<<ListboxSelect>>",
            self.on_slot_selected
        )

        # selected Pokémon information
        ttk.Label(
            main,
            textvariable=self.selected_var,
            anchor="w"
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 8)
        )

        # species
        ttk.Label(
            main,
            text="Species:"
        ).grid(
            row=4,
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
            row=4,
            column=1,
            sticky="ew",
            pady=4
        )

        # level
        ttk.Label(
            main,
            text="Level:"
        ).grid(
            row=5,
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
            row=5,
            column=1,
            sticky="w",
            pady=4
        )

        # moves
        self.move_dropdowns = {}

        for move_number in range(1, 5):
            row = 5 + move_number

            ttk.Label(
                main,
                text=f"Move {move_number}:"
            ).grid(
                row=row,
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
                row=row,
                column=1,
                sticky="ew",
                pady=4
            )

            self.move_dropdowns[move_number] = dropdown

        # Save As
        ttk.Button(
            main,
            text="Save As...",
            command=self.save_as
        ).grid(
            row=10,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(15, 5)
        )

        # status message
        ttk.Label(
            main,
            textvariable=self.status_var,
            anchor="center",
            wraplength=420
        ).grid(
            row=11,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(5, 0)
        )


    # --------------------------------------------------------
    # build party list
    # --------------------------------------------------------

    def refresh_slot_list(self, selected_slot=None):
        self.refreshing_slots = True
        self.slot_list.delete(0, tk.END)

        if self.save_data is None:
            self.refreshing_slots = False
            return

        for slot in range(1, POKEMON_SLOT_COUNT + 1):
            address = self.get_species_address(slot)
            species_id = self.save_data[address]

            species_name = self.species.get(
                species_id,
                f"Unknown ({species_id})"
            )

            self.slot_list.insert(
                tk.END,
                f"Slot {slot} — {species_name} (#{species_id})"
            )

        if selected_slot is not None:
            selected_slot = max(
                1,
                min(selected_slot, POKEMON_SLOT_COUNT)
            )

            self.slot_list.selection_set(selected_slot - 1)
            self.slot_list.activate(selected_slot - 1)
            self.slot_list.see(selected_slot - 1)

        self.refreshing_slots = False

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

        required_size = 0x1C21

        if len(data) < required_size:
            messagebox.showerror(
                "Invalid Save",
                f"The selected file is too small.\n\n"
                f"Expected at least {required_size:#x} bytes, "
                f"but found {len(data):#x} bytes."
            )
            return

        # requires a full party before loading the save
        # preventing issue of editing PC records due to record shifting, as PC edits don't stick properly
        party_count = data[0x0C30]

        if party_count != 6:
            messagebox.showerror(
                "Cannot Load Save",
                f"This save has {party_count} party Pokémon.\n\n"
                "The editor requires exactly 6 party Pokémon "
                "to edit Pokémon records reliably.\n\n"
                "Please ensure the party is full, save the game, "
                "and try again."
            )
            return

        self.save_data = data
        self.save_path = file_path

        self.current_slot = 1
        self.refresh_slot_list(selected_slot=1)
        self.update_fields_from_save()

        filename = os.path.basename(file_path)

        self.status_var.set(
            f"Loaded: {filename}"
        )

    # --------------------------------------------------------
    # clear editor fields
    # --------------------------------------------------------

    def clear_fields(self):
        self.species_var.set("")
        self.level_var.set("")

        for move_number in range(1, 5):
            self.move_vars[move_number].set("")

    # --------------------------------------------------------
    # read selected Pokémon from save
    # --------------------------------------------------------

    def update_fields_from_save(self):
        if self.save_data is None or self.current_slot is None:
            self.clear_fields()
            return

        slot = self.current_slot

        species_address = self.get_species_address(slot)
        level_address = self.get_level_address(slot)
        move_addresses = self.get_move_addresses(slot)

        species_id = self.save_data[species_address]
        level = self.save_data[level_address]

        species_name = self.species.get(
            species_id,
            f"Unknown ({species_id})"
        )

        self.species_var.set(species_name)
        self.level_var.set(str(level))

        for move_number, address in move_addresses.items():
            move_id = self.save_data[address]

            move_name = self.moves.get(
                move_id,
                f"Unknown (0x{move_id:02X})"
            )

            self.move_vars[move_number].set(move_name)

        self.selected_var.set(
            f"Editing Slot {slot}: "
            f"{species_name} (#{species_id})"
        )

    # --------------------------------------------------------
    # select another party Pokémon
    # --------------------------------------------------------

    def on_slot_selected(self, event=None):
        if self.refreshing_slots:
            return

        selection = self.slot_list.curselection()

        if not selection:
            return

        new_slot = selection[0] + 1

        if new_slot == self.current_slot:
            return

        old_slot = self.current_slot

        # preserve edits to the previous Pokémon in memory before loading the newly selected Pokémon
        if old_slot is not None:
            try:
                self.write_fields_to_slot(old_slot)

            except ValueError as error:
                self.refresh_slot_list(
                    selected_slot=old_slot
                )

                messagebox.showerror(
                    "Invalid Value",
                    str(error)
                )
                return

        self.current_slot = new_slot

        self.refresh_slot_list(
            selected_slot=new_slot
        )

        self.update_fields_from_save()

    # --------------------------------------------------------
    # validate and write Pokémon's fields
    # --------------------------------------------------------

    def write_fields_to_slot(self, slot):
        if self.save_data is None:
            raise ValueError("No save file is loaded.")

        species_address = self.get_species_address(slot)
        level_address = self.get_level_address(slot)
        move_addresses = self.get_move_addresses(slot)

        # validate species
        species_name = self.species_var.get()
        original_species_id = self.save_data[species_address]

        if species_name in self.species_by_name:
            species_id = self.species_by_name[species_name]

            if not 1 <= species_id <= 159:
                raise ValueError(
                    "Species ID must be between 1 and 159."
                )

        elif species_name == f"Unknown ({original_species_id})":
            # preserve an unknown species ID if unchanged
            species_id = original_species_id

        else:
            raise ValueError(
                "Please select a valid species."
            )

        # validate level
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

        # validate moves before writing any changes
        move_ids = {}

        for move_number, address in move_addresses.items():
            move_name = self.move_vars[move_number].get()
            original_move_id = self.save_data[address]

            if move_name in self.moves_by_name:
                move_id = self.moves_by_name[move_name]

            elif move_name == f"Unknown (0x{original_move_id:02X})":
                # preserve an unknown move ID if unchanged
                move_id = original_move_id

            else:
                raise ValueError(
                    f"Please select a valid move for Move {move_number}."
                )

            if not 0 <= move_id <= 0xFF:
                raise ValueError(
                    f"Move {move_number} has an invalid ID: "
                    f"0x{move_id:X}"
                )

            move_ids[move_number] = move_id

        # update slot if values are valid
        self.save_data[species_address] = species_id
        self.save_data[level_address] = level

        for move_number, address in move_addresses.items():
            self.save_data[address] = move_ids[move_number]

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

        if self.current_slot is None:
            messagebox.showwarning(
                "No Pokémon Selected",
                "The save does not contain a party Pokémon to edit."
            )
            return

        try:
            self.write_fields_to_slot(self.current_slot)

        except ValueError as error:
            messagebox.showerror(
                "Invalid Value",
                str(error)
            )
            return

        old_checksum = self.save_data[0x1C20]
        new_checksum = calculate_checksum(self.save_data)

        self.save_data[0x1C20] = new_checksum

        print(
            f"Checksum: "
            f"0x{old_checksum:02X} -> 0x{new_checksum:02X}"
        )

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


# ------------------------------------------------------------
# start program
# ------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditor(root)
    root.mainloop()