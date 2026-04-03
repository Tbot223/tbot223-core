from pathlib import Path
from tbot223_core import AppCore

# Define a simple division function for testing (will raise ZeroDivisionError for m=0)
def divide(n, m):
    return n / m

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[1] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize AppCore
    ap = AppCore(is_logging_enabled=True, base_dir=BASE_DIR)

    # Define number of tasks
    TASK_COUNT = 5000

    # Prepare tasks for the process pool executor
    tasks = [(divide, {"n": i+1, "m": i*2}) for i in range(TASK_COUNT)]

    # Execute tasks using process pool executor
    # chunk_size=None (default) runs the full task list in one executor.
    # chunk_size=0 enables automatic chunking based on task count and workers.
    results = ap.process_pool_executor(data=tasks, workers=2, override=False, timeout=1, chunk_size=0)

    # Check overall success and print results
    if results.success:
        print("completed")
    else:
        print(results.data)

    # Iterate through results and print errors if any
    for idx, res in enumerate(results.data):
        if res.success:
            pass
        else:
            print(f"task {idx} :{res.error}")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
