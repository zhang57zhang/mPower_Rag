"""Direct model download"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from download_sentence_transformers import main as download_model

success = download_model()
sys.exit(0 if success else 1)
