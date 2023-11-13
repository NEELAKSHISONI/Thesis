import os

# Define the database directory path
DATAVOL = "data/database_files"

def ensure_database_directory():
    # Check if the directory exists
    if not os.path.exists(DATAVOL):
        # If it doesn't exist, create it
        os.makedirs(DATAVOL)

    # Check if the directory is writable
    if os.access(DATAVOL, os.W_OK):
        print(f"The directory {DATAVOL} is writable.")
    else:
        print(f"The directory {DATAVOL} is not writable. Check permissions.")

if __name__ == "__main__":
    # Run the setup function when the script is executed
    ensure_database_directory()
