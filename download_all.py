"""
Master download script - Download all dependencies
"""
import sys
import subprocess
from pathlib import Path

def run_script(script_path):
    """Run a Python script and return success status"""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            capture_output=True,
            text=True,
            timeout=600
        )

        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"Script timeout: {script_path}")
        return False
    except Exception as e:
        print(f"Script error: {e}")
        return False

def main():
    """Main function"""
    base_dir = Path(__file__).parent

    print("=" * 70)
    print("mPower_Rag - Download All Dependencies")
    print("=" * 70)
    print(f"Base directory: {base_dir}")

    # Download options
    print("\nSelect what to download:")
    print("  1. Qdrant binary")
    print("  2. sentence-transformers model")
    print("  3. Both")
    print("  4. Check current status")
    print()

    choice = input("Enter choice (1-4): ").strip()

    qdrant_exe = base_dir / "qdrant.exe"
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    model_dir = base_dir / "models" / model_name.replace("/", "--")

    if choice == "1":
        # Download Qdrant
        script_path = base_dir / "download_qdrant_binary.py"
        if script_path.exists():
            print("\n" + "-" * 70)
            print("Downloading Qdrant...")
            print("-" * 70)
            success = run_script(script_path)
            print("\n" + "-" * 70)
            print(f"Qdrant download: {'SUCCESS' if success else 'FAILED'}")
            print("-" * 70)
        else:
            print(f"Script not found: {script_path}")

    elif choice == "2":
        # Download sentence-transformers model
        script_path = base_dir / "download_sentence_transformers.py"
        if script_path.exists():
            print("\n" + "-" * 70)
            print("Downloading sentence-transformers model...")
            print("-" * 70)
            success = run_script(script_path)
            print("\n" + "-" * 70)
            print(f"Model download: {'SUCCESS' if success else 'FAILED'}")
            print("-" * 70)
        else:
            print(f"Script not found: {script_path}")

    elif choice == "3":
        # Download both
        print("\n" + "-" * 70)
        print("Step 1/2: Downloading Qdrant...")
        print("-" * 70)

        script_path = base_dir / "download_qdrant_binary.py"
        qdrant_success = False
        if script_path.exists():
            qdrant_success = run_script(script_path)

        print("\n" + "-" * 70)
        print(f"Qdrant download: {'SUCCESS' if qdrant_success else 'FAILED'}")
        print("-" * 70)

        print("\n" + "-" * 70)
        print("Step 2/2: Downloading sentence-transformers model...")
        print("-" * 70)

        script_path = base_dir / "download_sentence_transformers.py"
        model_success = False
        if script_path.exists():
            model_success = run_script(script_path)

        print("\n" + "-" * 70)
        print(f"Model download: {'SUCCESS' if model_success else 'FAILED'}")
        print("-" * 70)

        # Summary
        print("\n" + "=" * 70)
        print("Download Summary")
        print("=" * 70)
        print(f"Qdrant: {'INSTALLED' if qdrant_success else 'FAILED'}")
        print(f"sentence-transformers: {'INSTALLED' if model_success else 'FAILED'}")

        if qdrant_success and model_success:
            print("\nAll downloads completed successfully!")
            print("\nNext steps:")
            print("  1. Start Qdrant: .\\qdrant.exe")
            print("  2. Initialize vector store: python init_vector_store.py")
            print("  3. Start API: python simple_api.py")
        elif qdrant_success:
            print("\nQdrant installed successfully!")
            print("\nNext steps:")
            print("  1. Start Qdrant: .\\qdrant.exe")
            print("  2. Start API: python simple_api.py")
            print("     (Will use local TF-IDF if model not available)")
        else:
            print("\nDownloads failed or incomplete")
            print("\nYou can still use local TF-IDF vector search.")
            print("Start API: python simple_api.py")

    elif choice == "4":
        # Check status
        print("\n" + "-" * 70)
        print("Current Status")
        print("-" * 70)

        print("\nQdrant:")
        if qdrant_exe.exists():
            size = qdrant_exe.stat().st_size
            print(f"  Status: INSTALLED")
            print(f"  Size: {size / 1024 / 1024:.1f} MB")
            print(f"  Path: {qdrant_exe}")
        else:
            print(f"  Status: NOT INSTALLED")
            print(f"  Path: {qdrant_exe}")

        print("\nSentence-transformers model:")
        if model_dir.exists():
            print(f"  Status: INSTALLED")
            print(f"  Path: {model_dir}")

            # List model files
            files = list(model_dir.glob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            print(f"  Files: {len(files)}")
            print(f"  Total size: {total_size / 1024 / 1024:.1f} MB")

            # Check key files
            key_files = ["config.json", "pytorch_model.bin", "tokenizer.json"]
            print("\n  Key files:")
            for filename in key_files:
                file_path = model_dir / filename
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"    {filename}: {size / 1024 / 1024:.1f} MB")
                else:
                    print(f"    {filename}: MISSING")
        else:
            print(f"  Status: NOT INSTALLED")
            print(f"  Path: {model_dir}")

        # Check git and git-lfs
        print("\nGit tools:")
        git_result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True
        )
        if git_result.returncode == 0:
            print(f"  git: {git_result.stdout.strip()}")
        else:
            print("  git: NOT INSTALLED")

        lfs_result = subprocess.run(
            ["git", "lfs", "version"],
            capture_output=True,
            text=True
        )
        if lfs_result.returncode == 0:
            print(f"  git-lfs: {lfs_result.stdout.strip()}")
        else:
            print("  git-lfs: NOT INSTALLED")

        print("\n" + "-" * 70)

    else:
        print("Invalid choice")

    print("\n" + "=" * 70)
    print("Done")
    print("=" * 70)

if __name__ == "__main__":
    main()
