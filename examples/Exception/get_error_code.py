# avoid `Exception` name conflict
from tbot223_core import Exception as Exc

if __name__ == "__main__":
    # Initialize ExceptionTracker
    tracker = Exc.ExceptionTracker()

    # Define custom error codes
    error_id_map = {
        "ZeroDivisionError": 1001,
        "ValueError": "ERR_VALUE",
        "KeyError": "ERR_KEY"
    }

    # Test mapped error code lookup
    try:
        10 / 0
    except Exception as e:
        error_code = tracker.get_error_code(error_id_map, e)
        print("ZeroDivisionError code:", error_code.data)

    # Test another mapped error code
    try:
        int("not_a_number")
    except Exception as e:
        error_code = tracker.get_error_code(error_id_map, e)
        print("ValueError code:", error_code.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
