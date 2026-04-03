import time
from tbot223_core import DecoratorUtils

if __name__ == "__main__":
    # Initialize DecoratorUtils
    decorator_utils = DecoratorUtils()

    # Apply runtime counter decorator
    @decorator_utils.count_runtime()
    def sample_work(delay: float):
        time.sleep(delay)
        return "Completed"

    result = sample_work(0.5)
    print("Function result:", result)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
