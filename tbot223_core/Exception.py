# external modules
import sys
import os
import platform
import time
import traceback
from typing import Any, Tuple, Callable, Union
from functools import wraps

# internal modules
from tbot223_core.Result import Result

class ExceptionTracker():
    """
    Collect structured exception information and return it in the project's
    `Result` format.

    Main responsibilities:
    - locate where an exception occurred
    - build a detailed error information payload
    - standardize exception returns for callers
    - map exception types to user-defined error codes
    """

    def __init__(self):
        # Cache system information
        # Safely get current working directory
        try:
            cwd = os.getcwd()
        except Exception:
            cwd = "<Permission Denied or Unavailable>"

        self._system_info = {
            "OS": platform.system(),
            "OS_version": platform.version(),
            "Release": platform.release(),
            "Architecture": platform.machine(),
            "Processor": platform.processor(),
            "Python_Version": platform.python_version(),
            "Python_Executable": sys.executable,
            "Current_Working_Directory": cwd
        }

    # L1 Methods
    def get_exception_location(self, error: Exception) -> Result:
        """
        Return the source location for an exception.

        Args:
            `error` (Exception): The exception object to track.

        Returns:
            Result: A Result object containing the location where the
                exception occurred.
                - Format (str): `'{file}', line {line}, in {function}`

        Example:
            >>> try:
            >>>     1 / 0
            >>> except Exception as e:
            >>>     location_result = tracker.get_exception_location(e)
            >>>     print(location_result.data)
            >>> # Output: 'script.py', line 10, in <module>
        """
        try:
            tb = traceback.extract_tb(error.__traceback__)
            frame = tb[-1]  # Most recent frame
            return Result(True, None, None, f"'{frame.filename}', line {frame.lineno}, in {frame.name}")
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_location, L1", tb_str)

    def get_exception_info(self, error: Exception, user_input: Any=None, params: Tuple[Tuple, dict]=((), {}), mask_tuple: Tuple[bool, ...] = ()) -> Result:
        """
        Build a detailed error information payload for an exception.

        The returned payload includes traceback, location information,
        timestamp, input context, and cached system information.

        Args:
            `error` : The exception object to track.
            `user_input` : User input context related to the exception. Defaults to `((), {})`.
            `params` : Additional call context related to the exception.
                Expected format: `(args, kwargs)`.
            `mask_tuple` : A tuple of booleans indicating which parts of the
                error information should be masked.

        Note:
            `mask_tuple` should follow this order:
            `("user_input", "params", "traceback", "computer_info")`.
            If an element is `True`, the corresponding field is masked.
            For example, `(True, False, True, False)` masks
            `user_input` and `traceback`.

        Returns:
            Result: A Result object containing a detailed exception payload.
                - `data` (dict): Structured exception information. See the
                  project README for the full `error_info` structure.

        Example:
            >>> try:
            >>>     def divide(a, b):
            >>>         return a / b
            >>>     a, b = 10, 0
            >>>     # This will raise a ZeroDivisionError
            >>>     divide(a, b)
            >>> except Exception as e:
            >>>     info_result = tracker.get_exception_info(e, user_input="Divide operation", params=((a, b), {"a": a, "b": b}), mask_tuple=(False, False, False, False))
            >>>     print(info_result.data)
            >>> # Output: structured error_info dictionary
        """
        try:
            if error is None:
                raise ValueError("The 'error' argument must be an Exception instance, not None.")
            if params is None or not isinstance(params, tuple) or not len(params) == 2 or not isinstance(params[0], tuple) or not isinstance(params[1], dict):
                raise ValueError("The 'params' argument must be a tuple of (args, kwargs).")
            if not isinstance(mask_tuple, tuple) or not all(isinstance(i, bool) for i in mask_tuple):
                raise ValueError("The 'mask_tuple' argument must be a tuple of booleans.")
            if len(mask_tuple) != 4:
                raise ValueError("The 'mask_tuple' argument must have exactly 4 boolean values.")

            tb = traceback.extract_tb(error.__traceback__)
            frame = tb[-1]  # Most recent frame
            frame2 = tb[0]  # Original frame

            def masking(index, return_value):
                return "<Masked>" if mask_tuple[index] else return_value

            error_info = {
                "success": False,
                "error":{
                    "type": type(error).__name__ if error else "UnknownError",
                    "message": str(error) if error else "No exception information available"
                },
                "location": {
                    "file": frame.filename if frame else "Unknown",
                    "line": frame.lineno if frame else -1,
                    "function": frame.name if frame else "Unknown"
                },
                "origin_location": {
                    "file": frame2.filename if frame2 else "Unknown",
                    "line": frame2.lineno if frame2 else -1,
                    "function": frame2.name if frame2 else "Unknown"
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "input_context": {
                    "user_input": masking(0, user_input),
                    "params": masking(1, {
                        "args": params[0] if params else (),
                        "kwargs": params[1] if params else {}
                    })
                },
                "id": None,  # Reserved for future use (to provide unique IDs for exceptions)
                "traceback": masking(2, ''.join(traceback.format_exception(type(error), error, error.__traceback__))),
                "computer_info": masking(3, self._system_info)
            }
            return Result(True, None, None, error_info)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_info, L1", tb_str)

    # L2 Methods
    def get_exception_return(self, error: Exception, user_input: Any=None, params: Tuple[Tuple, dict]=((), {}), mask_tuple: Tuple[bool, ...]=()) -> Result:
        """
        Build a standardized failure `Result` from an exception.

        This helper is intended for direct use inside `except` blocks.

        Args:
            `error` : The exception object to track.
            `user_input` : User input context related to the exception. Defaults to None.
            `params` : Additional call context related to the exception.
                Expected format: `(args, kwargs)`.
            `mask_tuple` : A tuple of booleans indicating which parts of the
                error information should be masked.

        Note:
            `mask_tuple` should follow this order:
            `("user_input", "params", "traceback", "computer_info")`.
            If an element is `True`, the corresponding field is masked.
            For example, `(True, False, True, False)` masks
            `user_input` and `traceback`.

        Returns:
            Result: A standardized failure `Result` containing exception
                details in `data`.

        Example:
            >>> try:
            >>>     1 / 0
            >>> except Exception as e:
            >>>     print(tracker.get_exception_return(e, user_input="Divide operation", params=((1, 0), {"a":1, "b":0}), True))
            >>> Result(False, 'ZeroDivisionError :division by zero', "'script.py', line 10, in <module>", '<Masked>')
        """
        try:
            effective_mask = mask_tuple if len(mask_tuple) == 4 else (False, False, False, False)
            return Result(False, f"{type(error).__name__} :{str(error)}", self.get_exception_location(error).data, self.get_exception_info(error, user_input, params, mask_tuple=effective_mask).data)
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_exception_return, L2", tb_str)

    def get_error_code(self, error_id_map: dict, error: Exception) -> Result:
        """
        Return a user-defined error code for a given exception type.

        Args:
            `error_id_map` (dict): A dictionary mapping exception type names (str) to error
                codes (any).
            `error` (Exception): The exception object to get the error code for.

        Note:
            `error_id_map` is a user-defined mapping table.
            Example:
            `{ "ZeroDivisionError": 1001, "ValueError": 1002, ... }`
            This allows each project to define its own exception codes.
            Codes may be any type that fits the project's needs, such as
            `int` or `str`.

        Returns:
            Result: A Result object containing the mapped error code.
                If the exception type is not present in `error_id_map`,
                the method returns `success=False`.

        Example:
            >>> error_id_map = {
            >>>     "ZeroDivisionError": 1001,
            >>>     "ValueError": 1002
            >>> }
            >>> try:
            >>>     1 / 0
            >>> except Exception as e:
            >>>     code_result = tracker.get_error_code(error_id_map, e)
            >>>     print(code_result.data)
            >>> # Output: 1001
        """
        try:
            if type(error).__name__ not in error_id_map:
                raise KeyError(f"Error type '{type(error).__name__}' not found in error_id_map.")
            else:
                return Result(True, None, None, error_id_map[type(error).__name__])
        except Exception as e:
            print("An error occurred while handling another exception. This may indicate a critical issue.")
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return Result(False, f"{type(e).__name__} :{str(e)}", "Core.ExceptionTracker.get_error_code, L2", tb_str)

class ExceptionTrackerDecorator():
    """
    Decorator that wraps a function with `ExceptionTracker`.

    - Converts uncaught exceptions into standardized `Result` objects.
    - Best suited for non-critical convenience wrappers because it adds
      tracking overhead.
    - Not ideal when the caller depends on side effects such as custom
      logging or cleanup behavior.

    Args:
        `mask_tuple` : A tuple indicating which exception details to mask.
            Defaults to `(False, False, False, False)`.
            Order: `(user_input, params, traceback, computer_info)`.
            If the format is invalid, the default tuple is used instead.
        `tracker` : An `ExceptionTracker` instance to reuse. If omitted, a new
            instance is created.

    Returns:
        If no exception occurs, returns the original function's return value.
        If an exception occurs, returns a Result object with exception details.

    Example:
        >>> tracker = ExceptionTracker()
        >>> @ExceptionTrackerDecorator(mask_tuple=(True, True, True, True), tracker=tracker)
        >>> def risky_function(x, y):
        >>>     return x / y
        >>> print(risky_function(10, y=0))
        >>> # Output: Result(False, 'ZeroDivisionError :division by zero', "'script.py', line 10, in risky_function", '<Masked>')
        >>> print(risky_function(10, y=0).data['params'])
        >>> # Output: ((10,), {'y': 0})
    """
    def __init__(self, mask_tuple: Tuple[bool, bool, bool, bool] = (False, False, False, False), tracker: ExceptionTracker=ExceptionTracker()):
        self.tracker = tracker or ExceptionTracker()
        self.mask_tuple = mask_tuple
        if not isinstance(self.mask_tuple, tuple) or not all(isinstance(i, bool) for i in self.mask_tuple):
            self.mask_tuple = (False, False, False, False)
        if len(self.mask_tuple) != 4:
            self.mask_tuple = (False, False, False, False)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Union[Any, Result]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Union[Any, Result]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Use the tracker to get standardized exception return
                return self.tracker.get_exception_return(error=e, params=(args, kwargs), mask_tuple=self.mask_tuple)
        return wrapper
