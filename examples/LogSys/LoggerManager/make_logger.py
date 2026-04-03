from pathlib import Path
from tbot223_core import LogSys

# Define base directory for logs
BASE_DIR = Path(__file__).parents[2] / ".OtherFiles" / "logs"
SECOND_LOG_DIR = "MakeLogger"  # Subdirectory for this example

if __name__ == "__main__":
    # Initialize Logger Manager
    logger_manager = LogSys.LoggerManager(base_dir=BASE_DIR, second_log_dir=SECOND_LOG_DIR)

    # Create a logger
    result = logger_manager.make_logger("MakeLogger", log_level=LogSys.logging.DEBUG)

    if result.success:
        print(result.data)  # Logger 'MakeLogger' created successfully.

    # Get the created logger (`make_logger` is not returning the logger instance)
    result = logger_manager.get_logger("MakeLogger")

    # Use the logger
    if result.success:
        logger = result.data
        logger.debug("This is a debug message from MakeLogger logger.")
        logger.info("This is an info message from MakeLogger logger.")
    else:
        print(f"Failed to get logger: {result.error}")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
