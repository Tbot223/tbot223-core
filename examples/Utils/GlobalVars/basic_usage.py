from pathlib import Path
from tbot223_core import GlobalVars

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize GlobalVars
    gv = GlobalVars(is_logging_enabled=True, base_dir=BASE_DIR)

    # Set and get values
    gv.set("project_name", "Core")
    gv.set("version", "3.1.1")
    print("project_name:", gv.get("project_name").data)

    # Check existence and list variables
    print("version exists:", gv.exists("version").data)
    print("All keys:", gv.list_vars().data)

    # Delete one value
    gv.delete("version")
    print("version exists after delete:", gv.exists("version").data)

    # Clear all values
    gv.clear()
    print("All keys after clear:", gv.list_vars().data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
