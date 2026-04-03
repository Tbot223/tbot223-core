# external Modules
import time
from functools import wraps
from typing import Callable, Any

# internal Modules
from tbot223_core.Exception import ExceptionTracker

class DecoratorUtils:
    """
    Collection of lightweight decorator helpers.
    """

    
    def __init__(self):
        self._exception_tracker = ExceptionTracker()

    # Internal Methods

    # external Methods
    @staticmethod
    def count_runtime():
        """
        Return a decorator that prints how long a function takes to run.
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                run_time = end_time - start_time
                print(f"This ran for {run_time:.4f} seconds.")
                return result
            return wrapper
        return decorator
