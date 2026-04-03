from pathlib import Path
from tbot223_core import Utils

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize Utils
    utils = Utils(is_logging_enabled=True, base_dir=BASE_DIR)

    # Convert string path to Path
    string_path = utils.str_to_path("sample/folder/file.txt")
    print("Converted path:", string_path.data)
    print("Converted type:", type(string_path.data))

    # If Path object is already given, it is returned as is
    path_obj = Path("already/path.txt")
    already_path = utils.str_to_path(path_obj)
    print("Already path object:", already_path.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
