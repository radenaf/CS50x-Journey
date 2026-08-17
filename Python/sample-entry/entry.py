import csv
import os
from datetime import datetime

DATABASE_FILE = "samples.csv"

def initialize_database():
    """Create database file with headers if it doesn't exist."""
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Sample Number', 'Condition', 'Timestamp'])

def get_sample_number():
    """Prompt for sample number in format 0000/YEAR."""
    while True:
        sample = input("Enter sample number (format 0000/YEAR): ").strip()
        if len(sample) == 9 and sample[4] == '/' and sample[:4].isdigit() and sample[5:].isdigit():
            return f"PC {sample}"
        print("Invalid format. Please use 0000/YEAR (e.g., 0001/2024)")

def get_condition():
    """Prompt for sample condition."""
    while True:
        condition = input("Enter sample condition: ").strip()
        if condition:
            return condition
        print("Condition cannot be empty.")

def save_to_database(sample_number, condition):
    """Save sample and condition to CSV database."""
    initialize_database()
    with open(DATABASE_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([sample_number, condition, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    print(f"✓ Saved: {sample_number} | Condition: {condition}")

def show_help():
    """Display help information and available commands."""
    print("\n=== Help ===")
    print("Available commands:")
    print("  help       - Show this help message")
    print("  quit       - Exit the program")
    print("  view       - Display all entries in the database")
    print("  export     - Export database to CSV file for Google Sheets")
    print("  remove     - Remove a specific entry by sample number")
    print()

def view_database():
    """Display all entries from the database in table format."""
    if not os.path.exists(DATABASE_FILE):
        print("Database is empty.")
        return

    with open(DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) <= 1:
        print("No entries in database.")
        return

    headers = rows[0]
    print("\n" + "=" * 80)
    print(f"{headers[0]:<20} {headers[1]:<30} {headers[2]:<30}")
    print("=" * 80)
    for row in rows[1:]:
        timestamp = row[2].split('.')[0] if '.' in row[2] else row[2]
        sample_display = row[0].replace("PC ", "") if row[0].startswith("PC ") else row[0]
        print(f"{sample_display:<20} {row[1]:<30} {timestamp:<30}")
    print("=" * 80 + "\n")

def export_to_sheets():
    """Export database to a CSV file for Google Sheets."""
    if not os.path.exists(DATABASE_FILE):
        print("Database is empty. Nothing to export.")
        return

    with open(DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) <= 1:
        print("No entries in database. Nothing to export.")
        return

    export_filename = f"samples_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(export_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"✓ Database exported to: {export_filename}")
    print("  You can now open this file in Google Sheets or Excel.")

def remove_entry():
    """Remove a specific entry by sample number."""
    if not os.path.exists(DATABASE_FILE):
        print("Database is empty.")
        return

    sample_to_remove = input("Enter sample number to remove (format 0000/YEAR): ").strip()
    if not (len(sample_to_remove) == 9 and sample_to_remove[4] == '/' and sample_to_remove[:4].isdigit() and sample_to_remove[5:].isdigit()):
        print("Invalid format. Please use 0000/YEAR (e.g., 0001/2024)")
        return
    sample_to_remove = f"PC {sample_to_remove}"

    with open(DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    headers = rows[0]
    new_rows = [headers]
    found = False

    for row in rows[1:]:
        if row[0] == sample_to_remove:
            found = True
        else:
            new_rows.append(row)

    if not found:
        print(f"Entry '{sample_to_remove}' not found.")
        return

    with open(DATABASE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    print(f"✓ Entry '{sample_to_remove}' has been removed.")

def main():
    """Main entry point."""
    import sys

    initialize_database()

    # Handle command-line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'view':
            view_database()
            return
        elif command == 'help':
            show_help()
            return
        elif command == 'export':
            export_to_sheets()
            return
        elif command == 'remove':
            remove_entry()
            return
        elif command == 'clear' or command == 'clearwr':
            if os.path.exists(DATABASE_FILE):
                os.remove(DATABASE_FILE)
                initialize_database()
                print("Database cleared.")
            return

    print("=== Sample Entry System ===")
    print("Type 'help' for available commands or press Enter to start.\n")

    while True:
        user_input = input("Enter sample number (format 0000/YEAR) or command: ").strip()

        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'help':
            show_help()
            continue
        elif user_input.lower() == 'view':
            view_database()
            continue
        elif user_input.lower() == 'export':
            export_to_sheets()
            continue
        elif user_input.lower() == 'clear' or user_input.lower() == 'clearwr':
            if os.path.exists(DATABASE_FILE):
                os.remove(DATABASE_FILE)
                initialize_database()
                print("Database cleared.")
            continue
        elif user_input.lower() == 'remove':
            remove_entry()
            continue
        elif not user_input:
            continue

        if len(user_input) == 9 and user_input[4] == '/' and user_input[:4].isdigit() and user_input[5:].isdigit():
            sample_number = f"PC {user_input}"
            condition = get_condition()
            save_to_database(sample_number, condition)
        else:
            print("Invalid format. Please use 0000/YEAR (e.g., 0001/2024)")

if __name__ == "__main__":
    main()
