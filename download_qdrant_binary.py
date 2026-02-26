"""
Download Qdrant binary from GitHub releases
Simplified version with better error handling
"""
import urllib.request
import urllib.error
import ssl
from pathlib import Path
import sys

def create_unverified_context():
    """Create unverified SSL context for download"""
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        return True
    except:
        return False

def download_with_retry(url, dest_path, max_retries=3):
    """Download with retry logic"""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            print(f"URL: {url}")
            print(f"Destination: {dest_path}")

            # Create unverified context if needed
            context = create_unverified_context()

            # Custom opener with longer timeout
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)

            # Download with progress
            def progress_callback(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(downloaded * 100 / total_size, 100)
                    mb_downloaded = downloaded / 1024 / 1024
                    mb_total = total_size / 1024 / 1024
                    print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='', flush=True)

            urllib.request.urlretrieve(url, dest_path, progress_callback)
            print()  # New line

            # Verify file
            if dest_path.exists():
                size = dest_path.stat().st_size
                print(f"Downloaded: {size / 1024 / 1024:.1f} MB")

                if size > 1000000:  # At least 1 MB
                    return True
                else:
                    print("File too small, may be incomplete")
                    return False
            else:
                print("File was not created")
                return False

        except urllib.error.URLError as e:
            print(f"\nURL Error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in 5 seconds...")
                import time
                time.sleep(5)
            else:
                print("Max retries reached")
                return False
        except Exception as e:
            print(f"\nError: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in 5 seconds...")
                import time
                time.sleep(5)
            else:
                print("Max retries reached")
                return False

    return False

def main():
    """Main function"""
    base_dir = Path(__file__).parent
    qdrant_exe = base_dir / "qdrant.exe"

    print("=" * 60)
    print("Download Qdrant Binary")
    print("=" * 60)
    print(f"Base directory: {base_dir}")
    print(f"Destination: {qdrant_exe}")

    # Check if already exists
    if qdrant_exe.exists():
        size = qdrant_exe.stat().st_size
        print(f"\nQdrant already exists: {size / 1024 / 1024:.1f} MB")
        response = input("Download anyway? (y/n): ")
        if response.lower() != 'y':
            print("Using existing Qdrant")
            return True

    # Download URL
    url = "https://github.com/qdrant/qdrant/releases/latest/download/qdrant-windows-amd64.exe"

    print("\nStarting download...")

    success = download_with_retry(url, qdrant_exe)

    if success:
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"\nQdrant downloaded to: {qdrant_exe}")
        print(f"\nTo start Qdrant:")
        print(f"  {qdrant_exe}")
        print(f"\nOr run:")
        print(f"  .\\qdrant.exe")
        print(f"\nAfter starting, run:")
        print(f"  python init_vector_store.py")
        print(f"  python simple_api.py")
        return True
    else:
        print("\n" + "=" * 60)
        print("FAILED!")
        print("=" * 60)
        print("\nManual download:")
        print(f"  1. Visit: {url}")
        print(f"  2. Download qdrant-windows-amd64.exe")
        print(f"  3. Save to: {base_dir}")
        print(f"  4. Run: .\\qdrant.exe")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
