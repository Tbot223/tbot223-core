from tbot223_core import Result

if __name__ == "__main__":
    # Successful unwrap_or
    success_result = Result(True, None, "unwrap_or example", ["real", "data"])
    print("Success data:", success_result.unwrap_or(["fallback"]))

    # Failed unwrap_or
    failed_result = Result(False, "Sample unwrap_or error", "unwrap_or example", None)
    print("Failure fallback:", failed_result.unwrap_or(["fallback"]))

    # Cancelled unwrap_or
    cancelled_result = Result(None, None, "unwrap_or cancelled example", None)
    print("Cancelled fallback:", cancelled_result.unwrap_or(["fallback"]))

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
