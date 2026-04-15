#external Modules
from typing import Any, NamedTuple, Optional

#internal Modules

class ResultUnwrapException(RuntimeError):
    """
    Raised when `unwrap()` or `expect()` is called on a `Result` that does not
    represent success.
    """
    def __init__(self, error, context, data):
        """
        Initialize the exception with the details stored in the `Result`.

        Args:
            error (Optional[str]): Error message associated with the failed result.
            context (Optional[str]): Additional context attached to the result.
            data (Any): Payload stored in the result.

        Returns:
            None

        Example:
            >>> try:
            >>>     result = Result(success=False, error="Some error", context="TestContext", data=None)
            >>>     result.unwrap()
            >>> except ResultUnwrapException as e:
            >>>     print(e)
            >>> # Output: Cannot unwrap Result: Some error, Context: TestContext, Data:
        """
        super().__init__(f"Cannot unwrap Result: {error}, Context: {context}, Data: {data}")
        self.error = error
        self.context = context
        self.data = data

class Result(NamedTuple):
    """
    Immutable container that represents the outcome of an operation.

    `Result` is implemented as a `NamedTuple`, so instances are lightweight,
    readable, and immutable once created. This makes it easier to pass results
    across application layers without accidentally changing their state.

    Attributes:
        `success` (Optional[bool]): Overall outcome of the operation.
            - `True` means the operation succeeded.
            - `False` means the operation failed.
            - `None` means the operation was cancelled or not executed.
        `error` (Optional[str]): Human-readable error message for failed results.
            - This field stores a string, not an exception object.
        `context` (Optional[str]): Additional context about the operation.
            - This may include an operation name, parameters, or relevant state.
        `data` (Any): Data returned from the operation.
            - The payload can be any type, depending on the operation.
            - On failure, this is often error detail data or `None`.

    Methods:
        `unwrap()`: Return `data` if successful, otherwise raise `ResultUnwrapException`.
        `expect(msg: str)`: Return `data` if successful, otherwise raise with an optional custom message.
        `unwrap_or(default: Any)`: Return `data` if successful, otherwise return `default`.

    Note:
        - `unwrap()`, `expect()`, and `unwrap_or()` are convenience methods for
          extracting data based on the result state.
        - In most application code, directly checking `success`, `error`, and
          `data` is recommended because it keeps control flow explicit and easy
          to read.
        - These helper methods are useful when you want concise handling, but
          they are not always the clearest choice in more complex logic.

    Recommended Usage:
        >>> result = Result(success=True, error=None, context="FetchData", data={"key": "value"})
        >>> if result.success:
        >>>     print("Operation succeeded with data:", result.data)
        >>> else:
        >>>     print("Operation failed with error:", result.error)
        >>> # Output: Operation succeeded with data: {'key': 'value'}
    """
    success: Optional[bool]
    error: Optional[str]
    context: Optional[str]
    data: Any

    def unwrap(self) -> Any:
        """
        Return the contained `data` if the result is successful.

        Returns:
            `Any`: The stored payload.

        Raises:
            ResultUnwrapException: If the result represents failure or cancellation.

        Example:
            >>> result = Result(success=True, error=None, context="FetchData", data={"key": "value"})
            >>> data = result.unwrap()
            >>> print(data)
            >>> # Output: {'key': 'value'}
        """
        if self.success is True:
            return self.data
        elif self.success is False:
            raise ResultUnwrapException(self.error, self.context, self.data)
        else:
            raise ResultUnwrapException("Operation was cancelled or not executed.", self.context, self.data)

    def expect(self, msg: str = "") -> Any:
        """
        Return the contained `data` if the result is successful.

        Args:
            `msg` : Optional message to use if the result is not successful.

        Returns:
            `Any`: The stored payload.

        Raises:
            ResultUnwrapException: If the result does not represent success.

        Example:
            >>> result = Result(success=True, error=None, context="FetchData", data={"key": "value"})
            >>> data = result.expect()
            >>> print(data)
            >>> # Output: {'key': 'value'}
        """
        if self.success is True:
            return self.data
        error_message = msg or self.error
        if error_message is None and self.success is None:
            error_message = "Operation was cancelled or not executed."
        raise ResultUnwrapException(error_message, self.context, self.data)

    def unwrap_or(self, default: Any) -> Any:
        """
        Return the contained `data` if successful; otherwise return `default`.

        Args:
            `default` (Any): Fallback value to return when the result is not successful.

        Returns:
            `Any`: The stored payload, or `default` if the result is not successful.

        Example:
            >>> result = Result(success=False, error="Not Found", context="FetchData", data=None)
            >>> data = result.unwrap_or({"key": "default_value"})
            >>> print(data)
            >>> # Output: {'key': 'default_value'}
        """
        if self.success is True:
            return self.data
        return default
