import shutil
from datetime import datetime
import os
import subprocess

# Function to run shell commands and capture output
def run_command(command, check=False):
    try:
        result = subprocess.run(command, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return (True, result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {' '.join(command)}: {e.stderr}")
        return (False, e.stderr)

# Checks for Git and SSH configuration
def check_git_installed():
    return run_command(['git', '--version'], check=True)[0]

def check_ssh_keys_exist():
    ssh_path = os.path.join(os.path.expanduser('~'), '.ssh')
    keys_exist = any(os.path.exists(os.path.join(ssh_path, key)) for key in ['id_rsa', 'id_rsa.pub', 'id_ed25519', 'id_ed25519.pub'])
    if not keys_exist:
        print(f"No SSH keys found in {ssh_path}. Generate them using 'ssh-keygen' in Git Bash and add them to your GitHub account.")
    return keys_exist

def check_ssh_agent_running():
    success, output = run_command(['ssh-add', '-l'])
    if 'The agent has no identities.' in output:
        print("SSH key is not added to the ssh-agent. Attempting to add it...")
        start_agent_success, _ = run_command(['eval', '$(ssh-agent -s)'])
        add_key_success, _ = run_command(['ssh-add', os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa')])
        if start_agent_success and add_key_success:
            print("SSH key added to ssh-agent successfully.")
            return True
        else:
            print("Failed to add SSH key to ssh-agent.")
            return False
    return success

def set_git_remote_url_to_ssh():
    success, output = run_command(['git', 'remote', '-v'])
    if "git@github.com:" not in output:
        https_url = [line.split()[1] for line in output.splitlines() if 'origin' in line and '(fetch)' in line][0]
        if 'github.com' in https_url:
            username_repo = https_url.split('/')[-2:]
            ssh_url = f"git@github.com:{'/'.join(username_repo)}"
            set_url_success, _ = run_command(['git', 'remote', 'set-url', 'origin', ssh_url])
            if set_url_success:
                print("Git remote URL set to use SSH.")
                return True
            else:
                print("Failed to set Git remote URL to SSH.")
                return False
    else:
        print("Git remote URL already uses SSH.")
        return True

def git_add_commit_push():
    run_command(['git', 'add', '.'])
    commit_success, _ = run_command(['git', 'commit', '-m', 'Automated commit by script'])
    if commit_success:
        push_success, push_output = run_command(['git', 'push'])
        if push_success:
            print("Changes pushed to GitHub successfully.")
        else:
            print(f"Failed to push changes to GitHub: {push_output}")
    else:
        print("Nothing to commit, or commit failed.")

# Backup operation
def create_backup():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    source_file = 'index.html'
    backup_folder = 'backups'
    destination_file = f'{backup_folder}/index_backup_{timestamp}.html'
    os.makedirs(backup_folder, exist_ok=True)
    shutil.copy2(source_file, destination_file)

def main():
    print("Creating backup...")
    create_backup()

    print("\nChecking Git installation...")
    if not check_git_installed():
        return
    
    print("\nChecking for SSH keys...")
    if not check_ssh_keys_exist():
        return
    
    print("\nChecking if SSH key is added to ssh-agent...")
    if not check_ssh_agent_running():
        return
    
    print("\nChecking if Git remote URL uses SSH...")
    if not set_git_remote_url_to_ssh():
        return
    
    print("\nAdding, committing, and pushing backup to GitHub...")
    git_add_commit_push()

if __name__ == "__main__":
    main()
