"""
deploy_hf.py — Upload project to HuggingFace Space, skipping venv and large folders.
Run: python deploy_hf.py
"""

from huggingface_hub import HfApi
import os

REPO_ID = "shraddhashaha/omni-support-env"
REPO_TYPE = "space"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))

# Patterns to IGNORE — anything matching these will be skipped
IGNORE_PATTERNS = [
    # Virtual environment — the #1 cause of failure (600MB+)
    "venv/**",
    "env/**",
    ".venv/**",
    # Python cache
    "**/__pycache__/**",
    "**/*.pyc",
    "**/*.pyo",
    "**/*.pyd",
    # Dev/test files
    "test_phase*.py",
    "scratch/**",
    # Git internals
    ".git/**",
    ".gitignore",
    # Local secrets
    ".env",
    # Local data / outputs (large)
    "data/**",
    "omni-grpo-output/**",
    # Build / packaging
    "dist/**",
    "build/**",
    "*.egg-info/**",
    "uv.lock",
    "pyproject.toml",
    # This script itself
    "deploy_hf.py",
    # Jupyter checkpoints
    ".ipynb_checkpoints/**",
]

def main():
    api = HfApi()

    # Verify auth
    try:
        user = api.whoami()
        print(f"[OK] Authenticated as: {user['name']}")
    except Exception as e:
        print(f"[ERROR] Auth failed: {e}")
        print("  Run: huggingface-cli login")
        return

    # Ensure space exists
    try:
        api.repo_info(repo_id=REPO_ID, repo_type=REPO_TYPE)
        print(f"[OK] Space {REPO_ID} found")
    except Exception:
        print(f"  Space not found, creating {REPO_ID}...")
        api.create_repo(repo_id=REPO_ID, repo_type=REPO_TYPE, space_sdk="docker", exist_ok=True)
        print(f"[OK] Space {REPO_ID} created")

    print(f"\nUploading from: {LOCAL_DIR}")
    print(f"Ignoring: venv/, __pycache__/, data/, .env, etc.")
    print("This may take 1–2 minutes for ~10MB of source files...\n")

    try:
        api.upload_folder(
            folder_path=LOCAL_DIR,
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            ignore_patterns=IGNORE_PATTERNS,
            commit_message="Deploy: source files only (no venv)",
        )
        print(f"\n[DONE] Upload complete!")
        print(f"   View your Space: https://huggingface.co/spaces/{REPO_ID}")
        print(f"   Live demo:       https://{REPO_ID.replace('/', '-')}.hf.space")
    except Exception as e:
        print(f"\n[ERROR] Upload failed: {e}")

if __name__ == "__main__":
    main()
