"""
Download dependencies using git
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None) -> bool:
    """Run command and return success status"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            return True
        else:
            print(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"Command timeout: {cmd}")
        return False
    except Exception as e:
        print(f"Command error: {e}")
        return False

def download_qdrant_git(base_dir: Path) -> bool:
    """Clone Qdrant repository"""
    print("\n" + "=" * 60)
    print("Downloading Qdrant using git")
    print("=" * 60)

    qdrant_dir = base_dir / "qdrant_repo"

    if qdrant_dir.exists():
        print(f"Qdrant repository already exists: {qdrant_dir}")
        return True

    url = "https://github.com/qdrant/qdrant.git"
    print(f"Cloning: {url}")
    print(f"Destination: {qdrant_dir}")

    success = run_command(f"git clone --depth 1 --single-branch {url} {qdrant_dir}")

    if success and qdrant_dir.exists():
        print("\nQdrant repository cloned successfully!")
        print(f"Repository: {qdrant_dir}")
        print("\nNote: You need to build Qdrant from source or download the binary.")
        print("For quick setup, download from: https://github.com/qdrant/qdrant/releases")
        return True
    else:
        print("\nFailed to clone Qdrant repository")
        return False

def download_sentence_transformers_git(base_dir: Path) -> bool:
    """Clone sentence-transformers repository"""
    print("\n" + "=" * 60)
    print("Downloading sentence-transformers using git")
    print("=" * 60)

    st_dir = base_dir / "sentence-transformers"

    if st_dir.exists():
        print(f"sentence-transformers repository already exists: {st_dir}")
        return True

    url = "https://github.com/UKPLab/sentence-transformers.git"
    print(f"Cloning: {url}")
    print(f"Destination: {st_dir}")

    success = run_command(f"git clone --depth 1 {url} {st_dir}")

    if success and st_dir.exists():
        print("\nsentence-transformers cloned successfully!")
        print(f"Repository: {st_dir}")

        # Install the package
        print("\nInstalling sentence-transformers...")
        success = run_command(f"pip install -e {st_dir}")
        if success:
            print("sentence-transformers installed successfully!")
            return True
        else:
            print("Failed to install sentence-transformers")
            return False
    else:
        print("\nFailed to clone sentence-transformers repository")
        return False

def download_model_files(base_dir: Path) -> bool:
    """Download model files using huggingface-cli or git lfs"""
    print("\n" + "=" * 60)
    print("Downloading model files")
    print("=" * 60)

    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    model_dir = base_dir / "models" / model_name.replace("/", "--")
    model_dir.mkdir(parents=True, exist_ok=True)

    # Method 1: Try huggingface-cli
    print("\nMethod 1: Using huggingface-cli")
    success = run_command(f"huggingface-cli download {model_name} --local-dir {model_dir} --local-dir-use-symlinks False")
    if success:
        print(f"\nModel downloaded to: {model_dir}")
        return True

    # Method 2: Try git lfs
    print("\nMethod 2: Using git lfs")
    temp_dir = base_dir / "temp_model"
    temp_dir.mkdir(exist_ok=True)

    # Check if git lfs is available
    if run_command("git lfs version"):
        print("git lfs is available")
        success = run_command(f"git lfs clone https://huggingface.co/sentence-transformers/{model_name} {temp_dir}")

        if success and temp_dir.exists():
            print(f"\nModel cloned to: {temp_dir}")
            print(f"Copying to: {model_dir}")

            import shutil
            try:
                # Copy files
                for item in temp_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, model_dir / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, model_dir / item.name, dirs_exist_ok=True)

                print("Model files copied successfully!")
                return True
            except Exception as e:
                print(f"Failed to copy model files: {e}")
                return False
        else:
            print("Failed to clone model with git lfs")
            return False
    else:
        print("git lfs is not available")
        return False

def check_git_installed() -> bool:
    """Check if git is installed"""
    return run_command("git --version")

def check_git_lfs_installed() -> bool:
    """Check if git lfs is installed"""
    return run_command("git lfs version")

def main():
    """Main function"""
    base_dir = Path(__file__).parent

    print("=" * 60)
    print("mPower_Rag - Download Dependencies (Git)")
    print("=" * 60)
    print(f"Base directory: {base_dir}")

    # Check prerequisites
    print("\n" + "-" * 60)
    print("Checking prerequisites")
    print("-" * 60)

    git_ok = check_git_installed()
    git_lfs_ok = check_git_lfs_installed()

    print(f"git: {'OK' if git_ok else 'NOT INSTALLED'}")
    print(f"git lfs: {'OK' if git_lfs_ok else 'NOT INSTALLED'}")

    if not git_ok:
        print("\ngit is not installed. Please install git first.")
        print("Download from: https://git-scm.com/downloads")
        return False

    if not git_lfs_ok:
        print("\ngit lfs is not installed. Installing...")
        run_command("git lfs install")

    # Download Qdrant repository
    qdrant_success = download_qdrant_git(base_dir)

    # Download sentence-transformers
    st_success = download_sentence_transformers_git(base_dir)

    # Download model files
    model_success = False
    if st_success:
        model_success = download_model_files(base_dir)

    # Summary
    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Qdrant repository: {'SUCCESS' if qdrant_success else 'FAILED'}")
    print(f"sentence-transformers: {'SUCCESS' if st_success else 'FAILED'}")
    print(f"Model files: {'SUCCESS' if model_success else 'FAILED'}")

    if model_success:
        print("\nAll downloads completed successfully!")
        print("\nNext steps:")
        print("  1. Download Qdrant binary from: https://github.com/qdrant/qdrant/releases")
        print("  2. Start Qdrant: .\\qdrant.exe")
        print("  3. Initialize vector store: python init_vector_store.py")
        print("  4. Start API: python simple_api.py")
    elif st_success:
        print("\nsentence-transformers installed!")
        print("\nNote: Model files not downloaded. Will download on first use.")
        print("Start API: python simple_api.py")
    else:
        print("\nDownloads failed.")
        print("\nYou can still use local TF-IDF vector search.")
        print("Start API: python simple_api.py")

    return st_success or model_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
