from pathlib import Path
from tbot223_core import Utils

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize Utils
    utils = Utils(is_logging_enabled=True, base_dir=BASE_DIR)

    # List example
    data_list = [1, 2, 3, 4, 5, 6]
    list_result = utils.insert_at_intervals(data_list, interval=2, insert="X", at_start=True)
    print("List result:", list_result.data)

    # String example
    data_str = "ABCDEFGHIJ"
    str_result = utils.insert_at_intervals(data_str, interval=3, insert="-", at_start=False)
    print("String result:", str_result.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
