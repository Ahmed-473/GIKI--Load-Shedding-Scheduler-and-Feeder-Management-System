import tkinter as tk
from tkinter import ttk, messagebox


class PowerUnit:  # Parent class for all campus power units
    def __init__(self, unit_id, name, load_kw):  # Constructor for common attributes
        if not unit_id.strip():  # Check empty ID
            raise ValueError("Unit ID cannot be empty.")
        if not name.strip():  # Check empty name
            raise ValueError("Unit name cannot be empty.")
        if load_kw <= 0:  # Check invalid load
            raise ValueError("Load must be greater than zero.")

        self.unit_id = unit_id  # Store unit ID
        self.name = name  # Store building name
        self._category = "General"  # Protected category
        self.__load_kw = load_kw  # Private load
        self.__off_count = 0  # Private OFF counter
        self.status = "ON"  # Current status
        self.reason = "Normal operation"  # Current reason

    def get_load(self):  # Return private load
        return self.__load_kw

    def set_load(self, new_load):  # Update load safely
        if new_load <= 0:  # Validate load
            raise ValueError("Load must be greater than zero.")
        self.__load_kw = new_load  # Set new load

    def get_off_count(self):  # Return OFF count
        return self.__off_count

    def increment_off_count(self):  # Increase OFF count
        self.__off_count += 1

    def get_category(self):  # Return category
        return self._category

    def set_status(self, status, reason):  # Set ON/OFF status and reason
        self.status = status
        self.reason = reason
        if status == "OFF":
            self.increment_off_count()

    def get_priority(self, time_slot):  # Default priority method
        return 3


class AcademicBuilding(PowerUnit):  # Child class for academic buildings
    def __init__(self, unit_id, name, load_kw):
        super().__init__(unit_id, name, load_kw)
        self._category = "Academic"

    def get_priority(self, time_slot):  # Override priority for academic buildings
        if time_slot in ["8 AM - 9 AM", "9 AM - 2 PM"]:
            return 1
        return 2


class ResidentialBuilding(PowerUnit):  # Child class for hostels
    def __init__(self, unit_id, name, load_kw):
        super().__init__(unit_id, name, load_kw)
        self._category = "Residential"

    def get_priority(self, time_slot):  # Override priority for residential buildings
        if time_slot in ["2 PM - 6 PM", "6 PM - 11 PM"]:
            return 1
        return 2


class UtilityBuilding(PowerUnit):  # Child class for utility building
    def __init__(self, unit_id, name, load_kw):
        super().__init__(unit_id, name, load_kw)
        self._category = "Utility"

    def get_priority(self, time_slot):  # Utility always lowest priority
        return 3


class ScheduleRecord:  # Class to store one schedule
    def __init__(self, time_slot, available_supply, total_demand, results):
        self.time_slot = time_slot
        self.available_supply = available_supply
        self.total_demand = total_demand
        self.deficit = max(0, total_demand - available_supply)
        self.results = results


class LoadSheddingScheduler:  # Main scheduling class
    def __init__(self):
        self.units = []
        self.history = []
        self.unit_map = {}

    def add_unit(self, unit):  # Add one unit
        if unit.unit_id in self.unit_map:
            raise ValueError(f"Duplicate unit ID '{unit.unit_id}' is not allowed.")
        self.units.append(unit)
        self.unit_map[unit.unit_id] = unit

    def load_default_giki_data(self):  # Add default buildings
        self.add_unit(AcademicBuilding("F1", "New Academic Block", 180))
        self.add_unit(ResidentialBuilding("F2", "Boys Hostel", 220))
        self.add_unit(ResidentialBuilding("F3", "Girls Hostel", 180))
        self.add_unit(AcademicBuilding("F4", "Faculty of Electrical", 140))
        self.add_unit(AcademicBuilding("F5", "Basic Sciences", 130))
        self.add_unit(AcademicBuilding("F6", "Mechanical", 160))
        self.add_unit(AcademicBuilding("F7", "Chemical", 150))
        self.add_unit(UtilityBuilding("F8", "GIKafe", 70))

    def calculate_total_demand(self):  # Compute total demand
        total = 0
        for unit in self.units:
            total += unit.get_load()
        return total

    def reset_statuses(self):  # Reset all statuses
        for unit in self.units:
            unit.status = "ON"
            unit.reason = "Normal operation"

    def sort_units_for_schedule(self, time_slot):  # Sort units by priority, fairness, load
        return sorted(
            self.units,
            key=lambda unit: (
                unit.get_priority(time_slot),
                -unit.get_off_count(),
                unit.get_load()
            )
        )

    def generate_schedule(self, time_slot, available_supply):  # Generate one schedule
        if available_supply < 0:
            raise ValueError("Available supply cannot be negative.")
        if len(self.units) == 0:
            raise ValueError("No buildings/feeders available.")

        self.reset_statuses()
        total_demand = self.calculate_total_demand()
        sorted_units = self.sort_units_for_schedule(time_slot)

        used_supply = 0
        results = []

        if total_demand <= available_supply:
            for unit in sorted_units:
                unit.set_status("ON", "Enough supply available")
        else:
            for unit in sorted_units:
                current_load = unit.get_load()
                priority = unit.get_priority(time_slot)

                if used_supply + current_load <= available_supply:
                    if priority == 1:
                        reason = "High priority feeder kept ON"
                    elif priority == 2:
                        reason = "Medium priority feeder kept ON"
                    else:
                        reason = "Supply available after higher priorities"
                    unit.set_status("ON", reason)
                    used_supply += current_load
                else:
                    if priority == 3:
                        reason = "Lowest priority feeder shed"
                    else:
                        reason = "Shed due to limited supply and fair rotation"
                    unit.set_status("OFF", reason)

        for unit in sorted_units:
            results.append({
                "id": unit.unit_id,
                "name": unit.name,
                "category": unit.get_category(),
                "load": unit.get_load(),
                "priority": unit.get_priority(time_slot),
                "status": unit.status,
                "reason": unit.reason
            })

        record = ScheduleRecord(time_slot, available_supply, total_demand, results)
        self.history.append(record)
        return record


class LoadSheddingGUI:  # GUI class
    def __init__(self, root):  # Constructor for GUI
        self.root = root
        self.root.title("GIKI Load Shedding Scheduler")
        self.root.geometry("980x650")

        self.scheduler = LoadSheddingScheduler()  # Create scheduler object
        self.scheduler.load_default_giki_data()  # Load default campus data

        self.create_widgets()  # Build GUI widgets

    def create_widgets(self):  # Create all labels, entries, buttons, and output area
        title = tk.Label(
            self.root,
            text="GIKI Load Shedding Scheduler",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(10, 2))

        credit = tk.Label(
            self.root,
            text="Made by Muhammad Ahmed",
            font=("Arial", 10, "italic")
        )
        credit.pack(pady=(0, 10))

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Select Time Slot:", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5)

        self.time_slot_var = tk.StringVar()
        self.time_slot_box = ttk.Combobox(
            top_frame,
            textvariable=self.time_slot_var,
            state="readonly",
            width=20
        )
        self.time_slot_box["values"] = ("8 AM - 9 AM", "9 AM - 2 PM", "2 PM - 6 PM", "6 PM - 11 PM")
        self.time_slot_box.current(0)
        self.time_slot_box.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(top_frame, text="Available Supply (kW):", font=("Arial", 11)).grid(row=0, column=2, padx=10, pady=5)

        self.supply_entry = tk.Entry(top_frame, width=15, font=("Arial", 11))
        self.supply_entry.grid(row=0, column=3, padx=10, pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Generate Schedule", width=18, command=self.generate_schedule_gui).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Show Buildings", width=15, command=self.show_buildings_gui).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="Clear Output", width=12, command=self.clear_output).grid(row=0, column=2, padx=5, pady=5)

        self.output_text = tk.Text(self.root, width=120, height=28, font=("Courier New", 10))
        self.output_text.pack(padx=10, pady=10)

    def clear_output(self):  # Clear text area
        self.output_text.delete("1.0", tk.END)

    def write_output(self, text):  # Write text in output box
        self.output_text.insert(tk.END, text + "\n")

    def show_buildings_gui(self):  # Display all campus buildings
        self.clear_output()
        self.write_output("================ GIKI CAMPUS FEEDERS ================")
        self.write_output(f"{'ID':<4} {'Building':<25} {'Category':<12} {'Load(kW)':<10} {'OFF Count':<10}")
        self.write_output("-" * 70)

        for unit in self.scheduler.units:
            line = f"{unit.unit_id:<4} {unit.name:<25} {unit.get_category():<12} {unit.get_load():<10} {unit.get_off_count():<10}"
            self.write_output(line)

        self.write_output("-" * 70)
        self.write_output(f"Total Connected Load: {self.scheduler.calculate_total_demand()} kW")

    def generate_schedule_gui(self):  # Generate schedule from GUI inputs
        try:
            time_slot = self.time_slot_var.get()
            supply_text = self.supply_entry.get().strip()

            if supply_text == "":
                raise ValueError("Please enter available supply.")

            available_supply = int(supply_text)

            record = self.scheduler.generate_schedule(time_slot, available_supply)

            self.clear_output()
            self.write_output("================ LOAD SHEDDING SCHEDULE ================")
            self.write_output(f"Time Slot        : {record.time_slot}")
            self.write_output(f"Available Supply : {record.available_supply} kW")
            self.write_output(f"Total Demand     : {record.total_demand} kW")
            self.write_output(f"Deficit          : {record.deficit} kW")
            self.write_output("-" * 100)
            self.write_output(f"{'ID':<4} {'Building':<25} {'Category':<12} {'Load':<8} {'Priority':<8} {'Status':<6} Reason")
            self.write_output("-" * 100)

            for item in record.results:
                line = (
                    f"{item['id']:<4} "
                    f"{item['name']:<25} "
                    f"{item['category']:<12} "
                    f"{item['load']:<8} "
                    f"{item['priority']:<8} "
                    f"{item['status']:<6} "
                    f"{item['reason']}"
                )
                self.write_output(line)

            self.write_output("=" * 100)

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))


root = tk.Tk()  # Create main Tkinter window
app = LoadSheddingGUI(root)  # Create GUI app object
root.mainloop()  # Start GUI event loop