"""
Download sentence-transformers model
Supports multiple methods
"""
import os
import sys
from pathlib import Path
import subprocess

def run_command(cmd, cwd=None, timeout=300):
    """Run command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timeout: {cmd}")
        return None
    except Exception as e:
        print(f"Command error: {e}")
        return None

def check_git_lfs():
    """Check if git lfs is installed"""
    result = run_command("git lfs version")
    return result and result.returncode == 0

def install_git_lfs():
    """Install git lfs"""
    print("Installing git lfs...")
    result = run_command("git lfs install")
    if result and result.returncode == 0:
        print("git lfs installed successfully")
        return True
    else:
        print("Failed to install git lfs")
        return False

def download_with_git_lfs(base_dir, model_name):
    """Download model using git lfs"""
    print("\n" + "=" * 60)
    print(f"Downloading model using git lfs: {model_name}")
    print("=" * 60)

    if not check_git_lfs():
        print("git lfs not found, installing...")
        if not install_git_lfs():
            print("Cannot install git lfs, trying alternative method...")
            return False

    model_dir = base_dir / "models" / model_name.replace("/", "--")
    temp_dir = base_dir / "temp_model"

    # Clean up temp directory if exists
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)

    # Clone the model repository
    url = f"https://huggingface.co/sentence-transformers/{model_name}"
    print(f"\nCloning from: {url}")
    print(f"Temporary directory: {temp_dir}")

    result = run_command(f"git lfs clone {url} {temp_dir}", timeout=600)

    if not result or result.returncode != 0:
        print("Failed to clone model")
        if result:
            print(f"Error: {result.stderr}")
        return False

    if not temp_dir.exists():
        print("Clone directory not created")
        return False

    print("Clone successful")

    # Create target directory
    model_dir.mkdir(parents=True, exist_ok=True)

    # Copy files
    print(f"\nCopying files to: {model_dir}")
    import shutil

    try:
        for item in temp_dir.iterdir():
            dest = model_dir / item.name
            if item.is_file():
                shutil.copy2(item, dest)
                print(f"  Copied: {item.name}")
            elif item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
                print(f"  Copied: {item.name}/")

        print("\nModel files copied successfully")

        # Clean up temp directory
        shutil.rmtree(temp_dir)
        print("Temporary directory cleaned")

        return True

    except Exception as e:
        print(f"Failed to copy files: {e}")
        return False

def download_with_huggingface_cli(base_dir, model_name):
    """Download model using huggingface-cli"""
    print("\n" + "=" * 60)
    print(f"Downloading model using huggingface-cli: {model_name}")
    print("=" * 60)

    # Check if huggingface-cli is available
    result = run_command("huggingface-cli --version")
    if not result or result.returncode != 0:
        print("huggingface-cli not found")
        return False

    model_dir = base_dir / "models" / model_name.replace("/", "--")

    # Download model
    cmd = f"huggingface-cli download {model_name} --local-dir {model_dir} --local-dir-use-symlinks False"
    print(f"\nRunning: {cmd}")

    result = run_command(cmd, timeout=600)

    if result and result.returncode == 0:
        print("\nModel downloaded successfully")
        return True
    else:
        print("Failed to download model")
        if result:
            print(f"Error: {result.stderr}")
        return False

def setup_model_cache(base_dir):
    """Setup model cache environment"""
    print("\n" + "=" * 60)
    print("Setting up model cache environment")
    print("=" * 60)

    model_dir = base_dir / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    # Set environment variables
    os.environ["TRANSFORMERS_CACHE"] = str(model_dir)
    os.environ["HF_HOME"] = str(model_dir)

    print(f"TRANSFORMERS_CACHE = {model_dir}")
    print(f"HF_HOME = {model_dir}")

    # Create config file for pip
    pip_config = base_dir / "pip.conf"
    with open(pip_config, "w") as f:
        f.write("[global]\n")
        f.write(f"cache-dir = {model_dir}\n")

    print(f"Created pip config: {pip_config}")

    return True

def verify_model(base_dir, model_name):
    """Verify model files exist"""
    print("\n" + "=" * 60)
    print("Verifying model files")
    print("=" * 60)

    model_dir = base_dir / "models" / model_name.replace("/", "--")

    if not model_dir.exists():
        print(f"Model directory not found: {model_dir}")
        return False

    # Required files
    required_files = [
        "config.json",
        "pytorch_model.bin",
        "tokenizer.json",
        "tokenizer_config.txt"
    ]

    missing_files = []
    for filename in required_files:
        file_path = model_dir / filename
        if not file_path.exists():
            missing_files.append(filename)
            print(f"  Missing: {filename}")
        else:
            print(f"  Found: {filename} ({file_path.stat().st_size / 1024 / 1024:.1f} MB)")

    if missing_files:
        print(f"\nMissing {len(missing_files)} required files")
        return False

    print("\nAll required files found")
    return True

def main():
    """Main function"""
    base_dir = Path(__file__).parent
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"

    print("=" * 60)
    print("Download sentence-transformers Model")
    print("=" * 60)
    print(f"Base directory: {base_dir}")
    print(f"Model: {model_name}")

    # Setup cache
    setup_model_cache(base_dir)

    # Check if already downloaded
    if verify_model(base_dir, model_name):
        print("\nModel already downloaded!")
        response = input("Download anyway? (y/n): ")
        if response.lower() != 'y':
            print("Using existing model")
            return True

    # Try different download methods
    success = False

    # Method 1: huggingface-cli
    print("\nTrying Method 1: huggingface-cli")
    success = download_with_huggingface_cli(base_dir, model_name)

    # Method 2: git lfs
    if not success:
        print("\nTrying Method 2: git lfs")
        success = download_with_git_lfs(base_dir, model_name)

    # Verify
    if success:
        if verify_model(base_dir, model_name):
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"\nModel downloaded to: {base_dir / 'models' / model_name.replace('/', '--')}")
            print("\nNext steps:")
            print("  1. Start API: python simple_api.py")
            print("  2. The model will be used automatically")
            return True
        else:
            print("\nModel downloaded but verification failed")
            return False
    else:
        print("\n" + "=" * 60)
        print("FAILED!")
        print("=" * 60)
        print("\nAll download methods failed")
        print("\nAlternatives:")
        print("  1. Install huggingface-cli: pip install huggingface-hub")
        print("  2. Install git-lfs: git lfs install")
        print("  3. Run this script again")
        print("\nOr let sentence-transformers download on first use")
        print("Start API: python simple_api.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
