import sys
import os

# This line lets Python find files in the src folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import create_table, save_entry, get_all_entries, get_entry

# Step 1: create the table
create_table()

# Step 2: save some test entries
print("\nSaving test entries...")
save_entry("API", "Application Programming Interface", "A set of rules that allows software systems to communicate.")
save_entry("LLM", "Large Language Model", "An AI model trained on large amounts of text data.")
save_entry("ICT", "Information and Communication Technology", "Technologies used to handle information and communication.")

# Step 3: retrieve all entries and display them
print("\n--- All entries in the database ---")
entries = get_all_entries()
for entry in entries:
    id, acronym, expansion, definition, created_at = entry
    print(f"\n  ID       : {id}")
    print(f"  Acronym  : {acronym}({expansion})")
    print(f"  Definition: {definition}")
    print(f"  Saved at : {created_at}")

# Step 4: look up one specific entry
print("\n--- Looking up 'API' specifically ---")
result = get_entry("API")
if result:
    print(f"  Found: {result[1]}({result[2]})")
else:
    print("  Not found.")