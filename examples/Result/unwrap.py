from tbot223_core import Result
from tbot223_core.Result import ResultUnwrapException

if __name__ == "__main__":
    # Successful unwrap
    success_result = Result(True, None, "Unwrap example", {"name": "unwrap"})
    print("Successful unwrap:", success_result.unwrap())

    # Failed unwrap
    failed_result = Result(False, "Sample unwrap error", "Unwrap example", {"step": "failure"})
    try:
        failed_result.unwrap()
    except ResultUnwrapException as e:
        print("Failed unwrap raised:", e)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
