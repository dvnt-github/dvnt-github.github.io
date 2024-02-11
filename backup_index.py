import shutil
from datetime import datetime
import os
import subprocess

# Generate a timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Define the source and destination file paths
source_file = 'index.html'
backup_folder = 'backups'
destination_file = f'{backup_folder}/index_backup_{timestamp}.html'

# Ensure the backup folder exists
os.makedirs(backup_folder, exist_ok=True)

# Copy the file
shutil.copy2(source_file, destination_file)

# Git commands to add, commit, and push the changes
try:
    # Add changes to git
    subprocess.run(['git', 'add', '.'], check=True)

    # Commit changes
    subprocess.run(['git', 'commit', '-m', f'Backup index.html at {timestamp}'], check=True)

    # Push changes to GitHub
    subprocess.run(['git', 'push'], check=True)

    print("Backup created and changes pushed to GitHub successfully.")
except subprocess.CalledProcessError as e:
    print(f'An error occurred while trying to run git commands: {e}')
