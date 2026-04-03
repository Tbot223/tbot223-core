from tbot223_core import Result
from tbot223_core.Result import ResultUnwrapException

if __name__ == "__main__":
    # Successful expect
    success_result = Result(True, None, "Expect example", [1, 2, 3])
    print("Successful expect:", success_result.expect())

    # Failed expect
    failed_result = Result(False, "Sample expect error", "Expect example", {"step": "failure"})
    try:
        failed_result.expect()
    except ResultUnwrapException as e:
        print("Failed expect raised:", e)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
