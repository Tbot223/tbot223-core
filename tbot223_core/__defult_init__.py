# external Modules

# internal Modules
from Exception import ExceptionTracker
from LogSys import *

class DefaultInit:
    def __init__(self):
        pass

    def __call__(self, target_instance, 
                 is_logging_enabled, is_debug_enabled,
                 base_dir, second_log_dir, logger_name, log_level=logging.INFO):
        target_instance._exception_tracker = ExceptionTracker()
        cache = SimpleSetting(base_dir, second_log_dir, logger_name, log_level)