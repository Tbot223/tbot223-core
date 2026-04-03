from pathlib import Path
from tbot223_core import GlobalVars

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize GlobalVars
    gv = GlobalVars(is_logging_enabled=True, base_dir=BASE_DIR)

    # Attribute access
    gv.user_name = "songhojin"
    gv.language = "ko"
    print("Attribute user_name:", gv.user_name)
    print("Attribute language:", gv.language)

    # Call syntax
    gv("theme", "dark")
    print("Call get theme:", gv("theme").data)

    # Cleanup
    gv.clear()

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
