import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


# ============================================================
# DATABASE
# ============================================================

def create_database():
    try:
        conn = sqlite3.connect("bmi_database.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror(
            "Database Error",
            f"Unable to create database:\n{e}"
        )


# ============================================================
# BMI CALCULATION
# ============================================================

def calculate_bmi():

    name = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()

    # --------------------------------------------------------
    # Validate Name
    # --------------------------------------------------------

    if not name:
        messagebox.showerror(
            "Input Error",
            "Please enter the user's name."
        )
        return

    # --------------------------------------------------------
    # Validate Weight and Height
    # --------------------------------------------------------

    try:
        weight = float(weight_text)
        height = float(height_text)

    except ValueError:
        messagebox.showerror(
            "Input Error",
            "Weight and height must be numeric values."
        )
        return

    # --------------------------------------------------------
    # Validate Positive Values
    # --------------------------------------------------------

    if weight <= 0:
        messagebox.showerror(
            "Input Error",
            "Weight must be greater than 0."
        )
        return

    if height <= 0:
        messagebox.showerror(
            "Input Error",
            "Height must be greater than 0."
        )
        return

    # --------------------------------------------------------
    # Calculate BMI
    # --------------------------------------------------------

    bmi = weight / (height ** 2)

    # --------------------------------------------------------
    # Classify BMI
    # --------------------------------------------------------

    if bmi < 18.5:
        category = "Underweight"
        result_color = "orange"

    elif bmi < 25:
        category = "Normal"
        result_color = "green"

    elif bmi < 30:
        category = "Overweight"
        result_color = "orange"

    else:
        category = "Obese"
        result_color = "red"

    # --------------------------------------------------------
    # Display Result
    # --------------------------------------------------------

    result_label.config(
        text=f"BMI: {bmi:.2f}\nCategory: {category}",
        fg=result_color
    )

    # --------------------------------------------------------
    # Save Record
    # --------------------------------------------------------

    save_record(
        name,
        weight,
        height,
        bmi,
        category
    )


# ============================================================
# SAVE RECORD
# ============================================================

def save_record(name, weight, height, bmi, category):

    try:
        conn = sqlite3.connect("bmi_database.db")
        cursor = conn.cursor()

        date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO bmi_records
            (name, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            weight,
            height,
            bmi,
            category,
            date
        ))

        conn.commit()
        conn.close()

    except sqlite3.Error as e:

        messagebox.showerror(
            "Database Error",
            f"Unable to save BMI record:\n{e}"
        )


# ============================================================
# VIEW OVERALL HISTORY
# ============================================================

def view_history():

    try:
        conn = sqlite3.connect("bmi_database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, date, weight, height, bmi, category
            FROM bmi_records
            ORDER BY date
        """)

        records = cursor.fetchall()

        conn.close()

    except sqlite3.Error as e:

        messagebox.showerror(
            "Database Error",
            f"Unable to read database:\n{e}"
        )

        return

    # --------------------------------------------------------
    # No Records
    # --------------------------------------------------------

    if not records:

        messagebox.showinfo(
            "History",
            "No BMI records found."
        )

        return

    # --------------------------------------------------------
    # Create History Window
    # --------------------------------------------------------

    history_window = tk.Toplevel(root)

    history_window.title(
        "Overall BMI History"
    )

    history_window.geometry(
        "850x450"
    )

    # --------------------------------------------------------
    # Treeview Columns
    # --------------------------------------------------------

    columns = (
        "Name",
        "Date",
        "Weight",
        "Height",
        "BMI",
        "Category"
    )

    tree = ttk.Treeview(
        history_window,
        columns=columns,
        show="headings"
    )

    # --------------------------------------------------------
    # Column Headings
    # --------------------------------------------------------

    for column in columns:

        tree.heading(
            column,
            text=column
        )

    # --------------------------------------------------------
    # Column Width
    # --------------------------------------------------------

    tree.column(
        "Name",
        width=120
    )

    tree.column(
        "Date",
        width=170
    )

    tree.column(
        "Weight",
        width=100
    )

    tree.column(
        "Height",
        width=100
    )

    tree.column(
        "BMI",
        width=100
    )

    tree.column(
        "Category",
        width=130
    )

    # --------------------------------------------------------
    # Insert Records
    # --------------------------------------------------------

    for record in records:

        tree.insert(
            "",
            tk.END,
            values=record
        )

    # --------------------------------------------------------
    # Scrollbar
    # --------------------------------------------------------

    scrollbar = ttk.Scrollbar(
        history_window,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(10, 0),
        pady=10
    )

    scrollbar.pack(
        side="right",
        fill="y",
        pady=10
    )


# ============================================================
# SHOW USER BMI TREND
# ============================================================

# ============================================================
# SHOW OVERALL BMI TREND
# ============================================================

def show_graph():

    try:
        conn = sqlite3.connect("bmi_database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, date, bmi
            FROM bmi_records
            ORDER BY date
        """)

        records = cursor.fetchall()

        conn.close()

    except sqlite3.Error as e:

        messagebox.showerror(
            "Database Error",
            f"Unable to read database:\n{e}"
        )

        return

    # --------------------------------------------------------
    # Check Records
    # --------------------------------------------------------

    if not records:

        messagebox.showinfo(
            "BMI Trend",
            "No BMI records found."
        )

        return

    # --------------------------------------------------------
    # Prepare Data
    # --------------------------------------------------------

    names = [
        record[0]
        for record in records
    ]

    dates = [
        record[1]
        for record in records
    ]

    bmi_values = [
        record[2]
        for record in records
    ]

    # --------------------------------------------------------
    # Create Graph
    # --------------------------------------------------------

    plt.figure(figsize=(12, 6))

    plt.plot(
        range(len(records)),
        bmi_values,
        marker="o",
        linewidth=2
    )

    # --------------------------------------------------------
    # Display User Name on Each Point
    # --------------------------------------------------------

    for i, (name, date, bmi) in enumerate(records):

        plt.annotate(
            name,
            (i, bmi),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=9
        )

    # --------------------------------------------------------
    # BMI Reference Lines
    # --------------------------------------------------------

    plt.axhline(
        y=18.5,
        linestyle="--",
        label="Underweight Limit"
    )

    plt.axhline(
        y=25,
        linestyle="--",
        label="Normal Limit"
    )

    plt.axhline(
        y=30,
        linestyle="--",
        label="Obese Limit"
    )

    # --------------------------------------------------------
    # X-Axis
    # --------------------------------------------------------

    plt.xticks(
        range(len(records)),
        dates,
        rotation=45
    )

    # --------------------------------------------------------
    # Labels
    # --------------------------------------------------------

    plt.title(
        "Overall BMI Trend - All Users"
    )

    plt.xlabel(
        "Date"
    )

    plt.ylabel(
        "BMI"
    )

    plt.legend()

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    plt.show()

# ============================================================
# CLEAR INPUT FIELDS
# ============================================================

def clear_fields():

    name_entry.delete(
        0,
        tk.END
    )

    weight_entry.delete(
        0,
        tk.END
    )

    height_entry.delete(
        0,
        tk.END
    )

    result_label.config(
        text="BMI: --\nCategory: --",
        fg="black"
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

# Create database first
create_database()


# ------------------------------------------------------------
# Create Main Window
# ------------------------------------------------------------

root = tk.Tk()

root.title(
    "BMI Calculator & Health Tracker"
)

root.geometry(
    "500x600"
)

root.resizable(
    False,
    False
)


# ============================================================
# TITLE
# ============================================================

title_label = tk.Label(
    root,
    text="BMI Calculator",
    font=("Arial", 24, "bold")
)

title_label.pack(
    pady=20
)


# ============================================================
# USER NAME
# ============================================================

name_label = tk.Label(
    root,
    text="User Name",
    font=("Arial", 12)
)

name_label.pack()

name_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 12)
)

name_entry.pack(
    pady=5
)


# ============================================================
# WEIGHT
# ============================================================

weight_label = tk.Label(
    root,
    text="Weight (kg)",
    font=("Arial", 12)
)

weight_label.pack(
    pady=(10, 0)
)

weight_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 12)
)

weight_entry.pack(
    pady=5
)


# ============================================================
# HEIGHT
# ============================================================

height_label = tk.Label(
    root,
    text="Height (m)",
    font=("Arial", 12)
)

height_label.pack(
    pady=(10, 0)
)

height_entry = tk.Entry(
    root,
    width=30,
    font=("Arial", 12)
)

height_entry.pack(
    pady=5
)


# ============================================================
# CALCULATE BUTTON
# ============================================================

calculate_button = tk.Button(
    root,
    text="Calculate BMI",
    command=calculate_bmi,
    width=20,
    font=("Arial", 12, "bold")
)

calculate_button.pack(
    pady=20
)


# ============================================================
# RESULT
# ============================================================

result_label = tk.Label(
    root,
    text="BMI: --\nCategory: --",
    font=("Arial", 16, "bold")
)

result_label.pack(
    pady=10
)


# ============================================================
# VIEW HISTORY BUTTON
# ============================================================

history_button = tk.Button(
    root,
    text="View Overall History",
    command=view_history,
    width=20,
    font=("Arial", 10)
)

history_button.pack(
    pady=5
)


# ============================================================
# GRAPH BUTTON
# ============================================================

graph_button = tk.Button(
    root,
    text="Show BMI Trend",
    command=show_graph,
    width=20,
    font=("Arial", 10)
)

graph_button.pack(
    pady=5
)


# ============================================================
# CLEAR BUTTON
# ============================================================

clear_button = tk.Button(
    root,
    text="Clear",
    command=clear_fields,
    width=20,
    font=("Arial", 10)
)

clear_button.pack(
    pady=5
)


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()