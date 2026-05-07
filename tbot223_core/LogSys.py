# external Modules
import os
from typing import Union, Any, Optional, Tuple
from pathlib import Path
import logging
import time as time_module
import warnings

# internal Modules
from tbot223_core.Result import Result
from tbot223_core.Exception import ExceptionTracker

class LoggerManager:
    """
    Create and manage named loggers backed by file and stream handlers.
    """
    def __init__(self, base_dir: Optional[Union[str, Path]]=None, second_log_dir: Union[str, Path]="default"):
        """
        Initialize the logger manager.
        """
        # Dictionary to hold logger instances
        self._loggers = {}
        self._exception_tracker = ExceptionTracker()

        # Initialize base directory for logs
        self._BASE_DIR = Path(base_dir) if base_dir is not None else Path.cwd() / "logs"
        os.makedirs(self._BASE_DIR, exist_ok=True)
        self.second_log_dir = Path(second_log_dir)

        # Record start time for log filenames
        self._started_time = time_module.strftime("%Y-%m-%d_%Hh-%Mm-%Ss", time_module.localtime())

    def make_logger(self, logger_name: str, log_level: Union[int, str]=logging.INFO, timestamp: Any = None, **kwargs) -> Result:
        """
        Create a named logger.

        Args:
            `logger_name` : Name of the logger.
            `log_level` : Logging level (default: logging.INFO).
            `timestamp` : Time string to include in log filename. Defaults to None.
                The legacy `time=` keyword is still accepted as a deprecated alias.

        Returns:
            Result: A Result object indicating success or failure of logger creation.

        Example:
            >>> logger_manager = LoggerManager()
            >>> result = logger_manager.make_logger("my_logger", logging.DEBUG)
            >>> if result.success:
            >>>     print(result.data) # Logger 'my_logger' created successfully.
            >>> else:
            >>>     print(result.error)
        """
        try:
            if "time" in kwargs:
                if timestamp is not None:
                    raise ValueError("Use either 'timestamp' or deprecated 'time', not both.")
                warnings.warn(
                    "LoggerManager.make_logger(time=...) is deprecated; use timestamp=... instead.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                timestamp = kwargs.pop("time")
            if kwargs:
                unexpected = ", ".join(sorted(kwargs.keys()))
                raise TypeError(f"Unexpected keyword argument(s): {unexpected}")

            # Duplicate check
            if logger_name in self._loggers:
                raise ValueError(f"Logger with name '{logger_name}' already exists.")

            # Always create a new logger instance
            self._loggers[logger_name] = logging.getLogger(logger_name)
            logger = self._loggers[logger_name]
            logger.setLevel(log_level)
            logger.propagate = False  # Prevent duplicate log output

            # Create a log file
            log_filename = self._BASE_DIR / self.second_log_dir / f"{timestamp or self._started_time}_log" / f"{logger_name}.log"
            os.makedirs(log_filename.parent, exist_ok=True)

            # Prevent duplicate handlers
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # Set formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # Set file handler
            file_handler = logging.FileHandler(log_filename)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Set console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            return Result(True, None, None, f"Logger '{logger_name}' created successfully.")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)

    def get_logger(self, logger_name: str) -> Result:
        """
        Return a logger by name.

        Args:
            `logger_name` : Name of the logger to retrieve.

        Returns:
            Result: A Result object containing the logger instance if found.

        Example:
            >>> logger_manager = LoggerManager()
            >>> logger_manager.make_logger("my_logger", logging.DEBUG)
            >>> result = logger_manager.get_logger("my_logger")
            >>> if result.success:
            >>>     logger = result.data
            >>>     logger.info("This is a test log message.")
            >>> else:
            >>>     print(result.error)
        """
        try:
            if logger_name not in self._loggers:
                raise ValueError(f"Logger with name '{logger_name}' does not exist.")
            return Result(True, None, None, self._loggers[logger_name])
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)

    def stop_stream_handlers(self, logger: logging.Logger) -> Result:
        """
        Remove the stream handler added by `LoggerManager.make_logger()`.

        **WARNING**:
            - This method assumes the stream handler is the second handler
              attached to the logger.
            - If the logger has a different handler layout, this method may
              not behave as expected.
            - The logger should be created by `LoggerManager.make_logger()`.

        Args:
            `logger` : Logger instance to stop stream handlers for.

        Returns:
            Result: A Result object indicating success or failure of the operation.

        Example:
            >>> logger_manager = LoggerManager()
            >>> logger_manager.make_logger("my_logger", logging.DEBUG)
            >>> logger_manager.stop_stream_handlers(logger)
        """
        try:
            if logger is None or not isinstance(logger, logging.Logger):
                raise ValueError("logger must be an instance of logging.Logger.")
            stream_handler = logger.handlers[1]  # Assuming the second handler is the stream handler
            stream_handler.close()
            logger.handlers.pop(1)
            return Result(True, None, None, "Stream handlers stopped successfully.")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)

class Log:
    """
    Thin wrapper around `logging.Logger` that returns project-style `Result`
    objects.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the wrapper with a logger instance.
        """
        self.logger = logger
        self._exception_tracker = ExceptionTracker()
        self.log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

    def log_message(self, level: Optional[Union[int, str]], message: str) -> Result:
        """
        Log a message with the specified log level.

        Args:
            `level` : Log level as an integer or string ('INFO').
            `message` : The message to log.

        Returns:
            Result: A Result object indicating success or failure of the logging operation.

        Example:
            >>> logger_manager = LoggerManager()
            >>> logger_result = logger_manager.make_logger("app_logger", logging.INFO)
            >>> if logger_result.success:
            >>>     logger = logger_result.data
            >>>     log_system = Log(logger)
            >>>     log_result = log_system.log_message('INFO', "This is an info message.")
            >>>     if log_result.success:
            >>>         print("Log message sent successfully.")
            >>>     else:
            >>>         print(log_result.error)
            >>> else:
            >>>     print(logger_result.error)
        """
        if self.logger is None:
            return Result(False, None, "Logger is not initialized.", None)
        try:
            if isinstance(level, str):
                level = self.log_levels.get(level.upper(), logging.INFO)
            if level is None:
                level = logging.INFO

            self.logger.log(level, message)
            return Result(True, None, None, "Log message sent successfully.")
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)

class SimpleSetting:
    """
    Convenience helper that creates `LoggerManager`, `Log`, and a named logger
    in one step.
    """
    def __init__(self, base_dir: Union[str, Path], second_log_dir: Union[str, Path], logger_name: str, log_level: Union[int, str] = logging.INFO):
        """
        Build the logging helper set in one call.

        Args:
            `base_dir` : Base directory for logs.
            `second_log_dir` : Subdirectory name within the base log directory.
            `logger_name` : Name of the logger to create.
            `log_level` : Logging level for the logger (default: logging.INFO).

        Returns:
            None

        Example:
            >>> setting = SimpleSetting("logs", "default", "app_logger")
            >>> logger_manager, log, logger = setting.get_instance()
        """
        self.logger_manager = LoggerManager(base_dir, second_log_dir)
        result = self.logger_manager.make_logger(logger_name, log_level=log_level)
        if result.success:
            self.logger = self.logger_manager.get_logger(logger_name).data
        else:
            self.logger = None
        self.log = Log(self.logger)

    def get_instance(self) -> Tuple[LoggerManager, Log, Optional[logging.Logger]]:
        """
        Return the initialized logging helpers.

        Returns:
            Tuple[LoggerManager, Log, logging.Logger]: The logger manager,
                wrapper, and logger instance.

        Example:
            >>> setting = SimpleSetting("logs", "default", "app_logger")
            >>> logger_manager, log, logger = setting.get_instance()
        """
        return self.logger_manager, self.log, self.logger
