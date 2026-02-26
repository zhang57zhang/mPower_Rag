"""
Download Qdrant and sentence-transformers from GitHub
"""
import urllib.request
import urllib.error
import zipfile
import tarfile
import os
import sys
from pathlib import Path
import tempfile

def download_file(url: str, dest_path: Path, show_progress: bool = True) -> bool:
    """Download file from URL"""
    try:
        print(f"Downloading: {url}")
        print(f"Save to: {dest_path}")

        def progress_callback(block_num, block_size, total_size):
            if total_size > 0 and show_progress:
                downloaded = block_num * block_size
                percent = min(downloaded * 100 / total_size, 100)
                mb_downloaded = downloaded / 1024 / 1024
                mb_total = total_size / 1024 / 1024
                print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='', flush=True)

        urllib.request.urlretrieve(url, dest_path, progress_callback)
        if show_progress:
            print()  # New line after progress

        print(f"Download complete: {dest_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True

    except urllib.error.URLError as e:
        print(f"\nDownload failed: {e}")
        return False
    except Exception as e:
        print(f"\nDownload failed: {e}")
        return False

def download_qdrant(base_dir: Path) -> bool:
    """Download Qdrant from GitHub"""
    print("\n" + "=" * 60)
    print("Downloading Qdrant from GitHub")
    print("=" * 60)

    # GitHub releases URL for Windows
    url = "https://github.com/qdrant/qdrant/releases/latest/download/qdrant-windows-amd64.exe"
    dest = base_dir / "qdrant.exe"

    if dest.exists():
        print(f"Qdrant already exists: {dest}")
        return True

    success = download_file(url, dest)

    if success and dest.exists() and dest.stat().st_size > 1000000:
        print("\nQdrant downloaded successfully!")
        print(f"\nTo start Qdrant:")
        print(f"  {dest}")
        return True
    else:
        print("\nQdrant download failed or file is invalid")
        return False

def download_sentence_transformer(base_dir: Path) -> bool:
    """Download sentence-transformers model from HuggingFace"""
    print("\n" + "=" * 60)
    print("Downloading sentence-transformers model")
    print("=" * 60)

    # HuggingFace model URL
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    base_url = f"https://huggingface.co/sentence-transformers/{model_name}/resolve/main"

    # Files to download
    files = [
        "config.json",
        "model_config.json",
        "pytorch_model.bin",
        "modules.json",
        "sentence_bert_config.json",
        "special_tokens_map.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "vocab.txt"
    ]

    # Create model directory
    model_dir = base_dir / "models" / model_name.replace("/", "--")
    model_dir.mkdir(parents=True, exist_ok=True)

    # Check if already downloaded
    config_file = model_dir / "config.json"
    if config_file.exists():
        print(f"Model already exists: {model_dir}")
        return True

    print(f"\nDownloading to: {model_dir}")
    print(f"Total files: {len(files)}")

    success_count = 0
    for i, filename in enumerate(files, 1):
        url = f"{base_url}/{filename}"
        dest = model_dir / filename

        print(f"\n[{i}/{len(files)}] Downloading {filename}...")
        if download_file(url, dest, show_progress=False):
            success_count += 1
        else:
            print(f"  Failed to download {filename}")

    print(f"\nDownloaded {success_count}/{len(files)} files")

    if success_count >= len(files) * 0.8:  # At least 80% success
        print("\nModel downloaded successfully!")
        return True
    else:
        print("\nModel download incomplete")
        return False

def setup_sentence_transformers_path(base_dir: Path):
    """Setup sentence-transformers to use local model"""
    print("\n" + "=" * 60)
    print("Setting up sentence-transformers local path")
    print("=" * 60)

    # Add model path to environment
    model_dir = base_dir / "models"
    if model_dir.exists():
        os.environ["TRANSFORMERS_CACHE"] = str(model_dir)
        os.environ["HF_HOME"] = str(model_dir)
        print(f"Set TRANSFORMERS_CACHE to: {model_dir}")
        print(f"Set HF_HOME to: {model_dir}")
        return True
    return False

def main():
    """Main function"""
    base_dir = Path(__file__).parent

    print("=" * 60)
    print("mPower_Rag - Download Dependencies")
    print("=" * 60)
    print(f"Base directory: {base_dir}")

    # Download Qdrant
    qdrant_success = download_qdrant(base_dir)

    # Download sentence-transformers model
    model_success = download_sentence_transformer(base_dir)

    if model_success:
        setup_sentence_transformers_path(base_dir)

    # Summary
    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Qdrant: {'SUCCESS' if qdrant_success else 'FAILED'}")
    print(f"sentence-transformers: {'SUCCESS' if model_success else 'FAILED'}")

    if qdrant_success and model_success:
        print("\nAll downloads completed successfully!")
        print("\nNext steps:")
        print("  1. Start Qdrant: .\\qdrant.exe")
        print("  2. Initialize vector store: python init_vector_store.py")
        print("  3. Start API: python simple_api.py")
    elif qdrant_success:
        print("\nQdrant downloaded successfully!")
        print("\nYou can still use local TF-IDF vector search.")
        print("Start API: python simple_api.py")
    else:
        print("\nDownloads failed.")
        print("You can still use local TF-IDF vector search.")
        print("Start API: python simple_api.py")

    return qdrant_success or model_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
