from pathlib import Path
from tbot223_core import LogSys

# Define base directory for logs
BASE_DIR = Path(__file__).parents[2] / ".OtherFiles" / "logs"
SECOND_LOG_DIR = "LogMessage"  # Subdirectory for this example

if __name__ == "__main__":
    # Initialize Logger Manager
    logger_manager = LogSys.LoggerManager(base_dir=BASE_DIR, second_log_dir=SECOND_LOG_DIR)

    # Create a logger
    result = logger_manager.make_logger("LogMessage", log_level=LogSys.logging.DEBUG)

    if result.success:
        print(result.data)  # Logger 'LogMessage' created successfully.

    # Get the created logger (`make_logger` is not returning the logger instance)
    result = logger_manager.get_logger("LogMessage")

    # Initialize Log
    log = LogSys.Log(result.data)

    # Use the logger
    if result.success:
        # enable Levels:
        # "WARNING", "ERROR", "CRITICAL", "DEBUG", "INFO"

        # Log messages with different levels ( use keyword arguments )
        log.log_message(level="DEBUG", message="This is a debug message from LogMessage logger.")
        log.log_message(level="INFO", message="This is an info message from LogMessage logger.")
        log.log_message(level="ERROR", message="This is an error message from LogMessage logger.")

        # Log a warning, critical message ( use positional arguments )
        log.log_message("WARNING", "This is a warning message from LogMessage logger.")
        log.log_message("CRITICAL", "This is a critical message from LogMessage logger.")
    else:
        print(f"Failed to get logger: {result.error}")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
