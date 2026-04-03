from pathlib import Path
from tbot223_core import LogSys

# Define base directory for logs
BASE_DIR = Path(__file__).parents[2] / ".OtherFiles" / "logs"
SECOND_LOG_DIR = "StopStreamHandlers"  # Subdirectory for this example

if __name__ == "__main__":
    # Initialize Logger Manager
    logger_manager = LogSys.LoggerManager(base_dir=BASE_DIR, second_log_dir=SECOND_LOG_DIR)

    # Create a logger for stopping stream handlers
    result = logger_manager.make_logger("StopStreamHandlers", log_level=LogSys.logging.DEBUG)

    if result.success:
        print(result.data)  # Logger 'StopStreamHandlers' created successfully.

    # Get the created logger (`make_logger` is not returning the logger instance)
    result = logger_manager.get_logger("StopStreamHandlers")

    # Use the logger
    if result.success:
        logger = result.data
        logger.debug("This is a debug message from StopStreamHandlers logger.")
        logger.info("This is an info message from StopStreamHandlers logger.")
    else:
        print(f"Failed to get logger: {result.error}")

    # Stop `StopStreamHandlers` logger stream handlers
    stop_result = logger_manager.stop_stream_handlers(logger)

    # Verify that stream handlers are stopped
    # These messages should not appear in the console
    if stop_result.success:
        logger.debug("This debug message should NOT appear in the console.")
        logger.info("This info message should NOT appear in the console.")
    else:
        print(f"Failed to stop stream handlers: {stop_result.error}")
        
    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
