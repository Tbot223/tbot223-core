from pathlib import Path
from tbot223_core import LogSys
import logging

# Define base directory for logs
BASE_DIR = Path(__file__).parents[2] / ".OtherFiles" / "logs"
SECOND_LOG_DIR = "SimpleSetting"  # Subdirectory for this example

if __name__ == "__main__":
    # Initialize with Simple Settings
    SimpleSetting = LogSys.SimpleSetting(base_dir=BASE_DIR, 
                                        second_log_dir=SECOND_LOG_DIR, 
                                        logger_name="SimpleSettingLogger", 
                                        log_level=logging.DEBUG)

    # Get the created logger
    log_manager, log, logger = SimpleSetting.get_instance()

    # Use the logger
    logger.info("This is an info message from SimpleSettingLogger.")
    logger.debug("This is a debug message from SimpleSettingLogger.") # This will appear because log level is set to DEBUG
    logger.setLevel(logging.INFO)
    logger.debug("This is a debug message from SimpleSettingLogger after changing log level to INFO.") # This will NOT appear

    # Use log instance to log messages
    log.log_message("ERROR", "This is an error message from SimpleSettingLogger.")
    log.log_message(level="WARNING", message="This is a warning message from SimpleSettingLogger.")

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
