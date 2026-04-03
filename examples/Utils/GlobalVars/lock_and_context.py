from pathlib import Path
from tbot223_core import GlobalVars

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize GlobalVars
    gv = GlobalVars(is_logging_enabled=True, base_dir=BASE_DIR)
    gv.set("counter", 0)

    # Use internal lock directly
    with gv.lock():
        current_value = gv.get("counter").data
        gv.set("counter", current_value + 1, overwrite=True)
    print("Counter after lock:", gv.get("counter").data)

    # Use GlobalVars as a context manager
    with gv:
        gv.set("context_value", "safe write", overwrite=True)
        print("Context value:", gv.get("context_value").data)

    # Cleanup
    gv.clear()

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
