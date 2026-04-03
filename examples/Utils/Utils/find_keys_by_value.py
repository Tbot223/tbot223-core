from pathlib import Path
from tbot223_core import Utils

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize Utils
    utils = Utils(is_logging_enabled=True, base_dir=BASE_DIR)

    # Non-nested dictionary example
    sample_dict = {"a": 1, "b": 3, "c": 1, "d": 5}
    equals_one = utils.find_keys_by_value(sample_dict, threshold=1, comparison="eq", nested=False)
    print("Equal to 1:", equals_one.data)

    # Nested dictionary example
    nested_dict = {
        "user_1": {"score": 70, "bonus": 10},
        "user_2": {"score": 95, "bonus": 25},
        "user_3": {"score": 88, "bonus": 30}
    }
    high_scores = utils.find_keys_by_value(
        nested_dict,
        threshold=80,
        comparison="gt",
        nested=True,
        separator="/",
        return_mod="path"
    )
    print("Greater than 80:", high_scores.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
