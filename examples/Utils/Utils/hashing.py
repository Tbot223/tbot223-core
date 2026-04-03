from pathlib import Path
from tbot223_core import Utils

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize Utils
    utils = Utils(is_logging_enabled=True, base_dir=BASE_DIR)

    # Sample text
    text = "Hello, Utils!"

    # Hash with multiple algorithms
    for algorithm in ["md5", "sha1", "sha256", "sha512"]:
        hashed = utils.hashing(text, algorithm=algorithm)
        print(f"{algorithm}: {hashed.data}")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
