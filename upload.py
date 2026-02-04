import os
import subprocess
from datetime import datetime

USERNAME = "Trend-daily"
REPO = "fbi"
BRANCH = "main"
SOURCE_DIR = "to_upload"
OUTPUT_FILE = "uploaded_links.txt"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.stdout.strip()

def ensure_dirs(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR)

def batch_upload():
    target_folder = input("Enter target folder inside repo (default: uploads): ").strip()
    if not target_folder:
        target_folder = "uploads"

    ensure_dirs(target_folder)

    files = os.listdir(SOURCE_DIR)
    if not files:
        print("No files to upload. Place images in 'to_upload/' and re-run.")
        return

    uploaded_links = []
    for filename in files:
        src_path = os.path.join(SOURCE_DIR, filename)
        dest_path = os.path.join(target_folder, filename)
        os.rename(src_path, dest_path)

        cdn_link = f"https://cdn.jsdelivr.net/gh/{USERNAME}/{REPO}@{BRANCH}/{target_folder}/{filename}"
        uploaded_links.append(cdn_link)
        print(f"Prepared: {cdn_link}")

    run_cmd("git add .")
    commit_msg = f"Batch upload to {target_folder} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_cmd(f'git commit -m "{commit_msg}"')
    run_cmd(f"git push origin {BRANCH}")

    with open(OUTPUT_FILE, "a") as f:
        for link in uploaded_links:
            f.write(link + "\n")

    print(f"\n✅ Uploaded {len(uploaded_links)} files to '{target_folder}'.")
    print(f"Links saved in {OUTPUT_FILE}")

if __name__ == "__main__":
    batch_upload()
