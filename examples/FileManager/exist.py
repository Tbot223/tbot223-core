from pathlib import Path
from tbot223_core import FileManager

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize FileManager
    fm = FileManager(base_dir=BASE_DIR, is_logging_enabled=True)

    # Prepare sample paths
    sample_dir = BASE_DIR / "ExistSampleDir"
    sample_file = sample_dir / "sample.txt"
    missing_file = sample_dir / "missing.txt"

    # Create sample directory and file
    fm.create_directory(sample_dir)
    fm.atomic_write(sample_file, "This file is used for exists example.")

    # Check paths
    file_exists = fm.exists(sample_file)
    dir_exists = fm.exists(sample_dir)
    missing_exists = fm.exists(missing_file)

    print("Existing file:", file_exists.data)
    print("Existing directory:", dir_exists.data)
    print("Missing file:", missing_exists.data)

    # Cleanup
    fm.delete_directory(sample_dir)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
