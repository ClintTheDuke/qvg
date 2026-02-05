import os
import subprocess
from datetime import datetime

SOURCE_DIR = "to_upload"
OUTPUT_FILE = "uploaded_links.txt"
BRANCH = "main"


def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def get_git_remote_info():
    """
    Extract GitHub USERNAME and REPO from the git remote URL.
    Supports HTTPS and SSH remotes.
    """
    url = run_cmd("git config --get remote.origin.url")

    if url.startswith("https://"):
        # https://github.com/USERNAME/REPO.git
        clean_url = url[:-4] if url.endswith(".git") else url
        parts = clean_url.split("/")
        return parts[-2], parts[-1]

    if url.startswith("git@"):
        # git@github.com:USERNAME/REPO.git
        repo_part = url.split(":")[1]
        repo_part = repo_part[:-4] if repo_part.endswith(".git") else repo_part
        username, repo = repo_part.split("/")
        return username, repo

    raise ValueError("Unsupported git remote URL format")


def ensure_dirs(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(SOURCE_DIR, exist_ok=True)


def batch_upload():
    try:
        username, repo = get_git_remote_info()
    except Exception as e:
        print("❌ Could not detect git remote info.")
        print(e)
        return

    target_folder = input(
        "Enter target folder inside repo (default: images/uploads): "
    ).strip()

    if not target_folder:
        target_folder = "images/uploads"

    ensure_dirs(target_folder)

    files = [
        f for f in os.listdir(SOURCE_DIR)
        if os.path.isfile(os.path.join(SOURCE_DIR, f))
    ]

    if not files:
        print("⚠️  No files found in 'to_upload/'")
        return

    uploaded_links = []

    for filename in files:
        src_path = os.path.join(SOURCE_DIR, filename)
        dest_path = os.path.join(target_folder, filename)

        os.rename(src_path, dest_path)

        cdn_link = (
            f"https://cdn.jsdelivr.net/gh/"
            f"{username}/{repo}@{BRANCH}/"
            f"{target_folder}/{filename}"
        )

        uploaded_links.append(cdn_link)
        print(f"Prepared → {cdn_link}")

    run_cmd("git add .")

    commit_msg = (
        f"Batch upload to {target_folder} "
        f"({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    )

    run_cmd(f'git commit -m "{commit_msg}"')
    run_cmd(f"git push origin {BRANCH}")

    with open(OUTPUT_FILE, "a") as f:
        for link in uploaded_links:
            f.write(link + "\n")

    print("\n✅ Upload complete")
    print(f"📁 Target folder: {target_folder}")
    print(f"🔗 Links saved to: {OUTPUT_FILE}")
    print(f"🌍 Repo detected: {username}/{repo}")


if __name__ == "__main__":
    batch_upload()
