from pathlib import Path
from unittest.mock import patch
from tbot223_core import AppCore

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize AppCore
    ap = AppCore(is_logging_enabled=True, base_dir=BASE_DIR)

    # Basic string input
    with patch("builtins.input", side_effect=["hello world"]):
        text_result = ap.safe_CLI_input(prompt="Enter text: ")
    print("Text input:", text_result.data)

    # Boolean input with valid option checking
    with patch("builtins.input", side_effect=["wrong", "yes"]):
        bool_result = ap.safe_CLI_input(
            prompt="Continue? ",
            input_type=bool,
            valid_options=["yes", "no"],
            case_sensitive=False,
            max_retries=2
        )
    print("Bool input:", bool_result.data)

    # Integer input with retry after empty input
    with patch("builtins.input", side_effect=["", "42"]):
        int_result = ap.safe_CLI_input(
            prompt="Enter number: ",
            input_type=int,
            allow_empty=False,
            max_retries=2
        )
    print("Integer input:", int_result.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
