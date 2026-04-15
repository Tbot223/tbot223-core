#external Modules
from typing import List, Union, Any, Optional
from pathlib import Path
import tempfile
import json
import shutil
import stat
import os
import logging
import warnings
if os.name != 'nt':
    import fcntl
else:
    import msvcrt

#internal Modules
from tbot223_core.Result import Result
from tbot223_core.Exception import ExceptionTracker
from tbot223_core.LogSys import LoggerManager, Log
from tbot223_core.Utils.Utils import Utils
from tbot223_core._default_init import DefaultInit

class FileManager:
    """
    File-system helper for safe reads, writes, directory operations, and JSON
    handling.
    """

    # File locking threshold: files larger than this size will be locked during read operations
    LOCK_FILE_SIZE_THRESHOLD = 10 * 1024 * 1024  # 10 MB

    def __init__(self, is_logging_enabled: bool=True, is_debug_enabled: bool=False, 
                 base_dir: Union[str, Path]=None,

                 DefaultInit: Optional[DefaultInit]=DefaultInit,
                 Utils: Optional[Utils]=Utils
                 ):
        """
        Initialize the AppCore instance with logging, exception tracking, and language support.

        - **(R) = Required argument**
        - **(O) = Optional argument (has a default value)**
        - **(D) = Dependency Injection (advanced usage)**
    
        Args:
            (O)`is_logging_enabled` (bool): Flag to enable or disable logging. Default is True
            (O)`is_debug_enabled` (bool): Flag to enable or disable debug mode. Default is False
            (O)`default_lang` (str): The default language code to use for localization. Default is
                "en".
            (O)`base_dir` (Union[str, Path]): Base directory for log files and language files. Default is
                the current working directory.

        

        """

        # Initialize paths
        self._BASE_DIR = Path(base_dir) if base_dir is not None else Path.cwd()

        # Initialize logging and exception tracking using DefaultInit
        DefaultInit.run(self, 
            is_logging_enabled=is_logging_enabled, 
            is_debug_enabled=is_debug_enabled, 
            base_dir=self._BASE_DIR / "logs", second_log_dir="file_manager", logger_name="FileManagerLogger", log_level="AUTO"
        )
        self._utils = Utils()

        self._log("INFO", f"FileManager initialized.")

    # internal Methods
    @staticmethod
    def _handle_exc(func, path, exc_info):
        """
        Retry a file-system operation after relaxing read-only permissions.

        Args:
            `func` : The function to retry.
            `path` : The path to the file or directory.
            `exc_info` : Exception information from the failed operation.

        Example:
            >>> file_manager._handle_exc(os.remove, "some/protected/file.txt", exc_info)
        """
        exc_type, exc_value, exc_tb = exc_info
        if not issubclass(exc_type, PermissionError):
            raise exc_value
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def _str_to_path(self, path: Any) -> Path:
        """
        Convert a string path to a `Path` object.

        Args:
            `path` : The path to convert.

        Returns:
            Path: The converted path object.

        Example:
            >>> path_obj = file_manager._str_to_path("some/directory/file.txt")
            >>> print(type(path_obj))
            >>> # Output: <class 'pathlib.Path'>
        """
        if isinstance(path, Path):
            return path
        return self._utils.str_to_path(path).data

    @staticmethod
    def _lock(file: Path, mode: int):
        """
        Apply or release a file lock.

        Args:
            `file` : Open file object to lock.
            `mode` : Lock mode.
                UNIX: `1` for `LOCK_EX`, `0` for `LOCK_UN`, `2` for `LOCK_SH`
                WINDOWS: `1` for `LK_LOCK`, `0` for `LK_UNLCK`

        Returns:
            This method does not return any value.

        Example:
            >>> with open("example.txt", "r+") as f:
            >>>     file_manager._lock(f, 1)  # Lock the file
            >>>     # Perform file operations
            >>>     file_manager._lock(f, 0)  # Unlock the file
        """
        if os.name != 'nt':
            if mode == 1:
                fcntl.flock(file, fcntl.LOCK_EX)
            elif mode == 2:
                fcntl.flock(file, fcntl.LOCK_SH)
            else:
                fcntl.flock(file, fcntl.LOCK_UN)
        else:
            if mode == 1:
                msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, os.path.getsize(file.name))
            elif mode == 2:
                lock_mode = msvcrt.LK_RLCK if hasattr(msvcrt, "LK_RLCK") else msvcrt.LK_LOCK
                msvcrt.locking(file.fileno(), lock_mode, os.path.getsize(file.name))
            else:
                msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, os.path.getsize(file.name))


    def atomic_write(self, file_path: Union[str, Path], data: Any) -> Result:
        """
        Atomically write data to a file.

        - If data is bytes, write in binary mode; if str, write in text mode with utf-8 encoding.
        - Use a temporary file in the same directory and rename it to ensure atomicity.
        - Ensure that the parent directory of file_path exists; create it if it does not.
        - Flush and sync data to disk before renaming to minimize data loss risk.

        Args:
            `file_path` : The path to the file where data will be written.
            `data` : The data to write to the file. Can be str or bytes.

        Returns:
            Result: A Result object indicating success or failure of the write operation.

        Example:
            >>> result = file_manager.atomic_write("example.txt", "Hello, World!")
            >>> if result.success:
            >>>     print("Write successful!")
            >>> else:
            >>>     print(f"Write failed: {result.error_message}")
        """
        temp_path = None
        try:
            file_path = self._str_to_path(file_path)
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)

            is_bytes = isinstance(data, bytes)
            mode = 'wb' if is_bytes else 'w'
            encoding = None if is_bytes else 'utf-8'

            def replace_temp_with_target(temp_path: Path, target_path: Path):
                if os.name == 'nt':
                    os.replace(temp_path, target_path)
                    return
                with open(target_path, "a+b") as f:
                    self._lock(f, 1)
                    try:
                        os.replace(temp_path, target_path)
                    finally:
                        self._lock(f, 0)

            with tempfile.NamedTemporaryFile(mode, delete=False, dir=str(file_path.parent), encoding=encoding) as temp:
                temp_path = Path(temp.name)
                temp.write(data)
                temp.flush()
                try:
                    os.fsync(temp.fileno())
                except (AttributeError, OSError):
                    pass  # os.fsync not available on some platforms
                temp.close()
                replace_temp_with_target(temp_path, file_path)

            self._log("INFO", f"Successfully wrote to {file_path}")
            return Result(True, None, None, f"Successfully wrote to {file_path}")
        except Exception as e:
            self._log("ERROR", f"Failed to write to {file_path}: {e}")
            try:
                if temp_path is not None and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    self._log("INFO", f"Temporary file {temp_path} deleted.")
            except Exception as ex:
                self._log("ERROR", f"Failed to delete temporary file {temp_path}: {ex}")
            return self._exception_tracker.get_exception_return(e)

    def read_file(self, file_path: Union[str, Path], as_bytes: bool=False) -> Result:
        """
        Read a file from disk.

        - If as_bytes is True, read in binary mode; otherwise, read in text mode with utf-8 encoding.
        - Return the content in the data field of the Result object.
        - Use file locking to ensure safe read operations.

        Args:
            `file_path` : The path to the file to read.
            `as_bytes` : If True, read the file in binary mode.

        Returns:
            Result: A Result object containing the file content in the data field.

        Example:
            >>> result = file_manager.read_file("example.txt")
            >>> if result.success:
            >>>     print(result.data)
            >>> else:
            >>>     print(f"Read failed: {result.error_message}")
        """
        try:
            file_path = self._str_to_path(file_path)

            mode = 'rb' if as_bytes else 'r'
            encoding = None if as_bytes else 'utf-8'
            LOCK = (os.path.getsize(file_path) > self.LOCK_FILE_SIZE_THRESHOLD)

            def safe_read(f, lock):
                if lock:
                    self._lock(f, 2)
                try:
                    content = f.read()
                finally:
                    if lock:
                        self._lock(f, 0)
                return content

            with open(file_path, mode, encoding=encoding) as f:
                content = safe_read(f, LOCK)

            self._log("INFO", f"Successfully read from {file_path}")
            return Result(True, None, None, content)
        except Exception as e:
            self._log("ERROR", f"Failed to read from {file_path}: {e}")
            return self._exception_tracker.get_exception_return(e)

    def write_json(self, file_path: Union[str, Path], data: Any, indent: int=4) -> Result:
        """
        Serialize JSON-compatible data and write it to disk.

        - Use atomic_write to ensure atomicity.
        - Pretty-print JSON with specified indentation.

        Args:
            `file_path` : The path to the file where JSON data will be written.
            `data` : The JSON serializable data to write to the file.
            `indent` (int, optional): Number of spaces for indentation in the JSON file. Defaults to 4.

        Returns:
            Result: A Result object indicating success or failure of the write operation.

        Example:
            >>> data = {"name": "Alice", "age": 30}
            >>> result = file_manager.write_json("data.json", data)
            >>> if result.success:
            >>>     print("JSON write successful!")
            >>> else:
            >>>     print(f"JSON write failed: {result.error_message}")
        """
        try:
            file_path = self._str_to_path(file_path)
            json_data = json.dumps(data, indent=indent, ensure_ascii=False)
            write_result = self.atomic_write(file_path, json_data)
            if not write_result.success:
                return write_result

            self._log("INFO", f"Successfully wrote JSON to {file_path}")
            return Result(True, None, None, f"Successfully wrote JSON to {file_path}")
        except Exception as e:
            self._log("ERROR", f"Failed to write JSON to {file_path}: {e}")
            return self._exception_tracker.get_exception_return(e)

    def read_json(self, file_path: Union[str, Path]) -> Result:
        """
        Read a JSON file and parse it into a Python object.

        - Return the parsed object in the data field of the Result object.

        Args:
            `file_path` : The path to the JSON file to read.

        Returns:
            Result: A Result object containing the parsed JSON data in the data field.

        Example:
            >>> result = file_manager.read_json("data.json")
            >>> if result.success:
            >>>     print(result.data)
            >>> else:
            >>>     print(f"JSON read failed: {result.error_message}")
        """
        try:
            file_path = self._str_to_path(file_path)
            if file_path.exists() is False:
                raise FileNotFoundError(f"File not found: {file_path}")
            if file_path.suffix.lower() != '.json':
                raise ValueError("File extension is not .json")

            read_result = self.read_file(file_path)
            if not read_result.success:
                return read_result

            self._log("INFO", f"Successfully read JSON from {file_path}")
            return Result(True, None, None, json.loads(read_result.data))
        except Exception as e:
            self._log("ERROR", f"Failed to read JSON from {file_path}: {e}")
            return self._exception_tracker.get_exception_return(e)

    def list_of_files(self, dir_path: Union[str, Path], extensions: List[str]=None, only_name: bool = False) -> Result:
        """
        List files in a directory.

        - If `extensions` is provided, filter files by those extensions
          case-insensitively.
        - If `only_name` is `True`, return file stems instead of full paths.

        Args:
            `dir_path` : The path to the directory to list files from.
            `extensions` : List of file extensions to filter by. Defaults to None (no filtering).
            `only_name` : If True, return only file names instead of full paths. Defaults to False.

        Returns:
            Result: A Result object containing the list of file paths or names in the data field.

        Example:
            >>> result = file_manager.list_of_files("some/directory", extensions=[".txt", ".md"], only_name=True)
            >>> if result.success:
            >>>     print(result.data)
            >>> else:
            >>>     print(f"Listing files failed: {result.error_message}")
        """
        try:
            dir_path = self._str_to_path(dir_path)
            extensions = [ext.lower() for ext in extensions] if extensions else []

            if not dir_path.is_dir():
                raise NotADirectoryError(f"Not a directory: {dir_path}")

            def is_matching_file(item: Path, list_obj: list):
                if extensions == [] or item.suffix.lower() in extensions:
                    list_obj.append(item.stem if only_name else str(item))

            files = []
            for item in dir_path.iterdir():
                if item.is_dir():
                    continue
                is_matching_file(item, files)

            self._log("INFO", f"Successfully listed files in {dir_path}")
            return Result(True, None, None, files)
        except Exception as e:
            self._log("ERROR", f"Failed to list files in {dir_path}: {e}")
            return self._exception_tracker.get_exception_return(e)

    def exists(self, path: Union[str, Path]) -> Result:
        """
        Check whether a file or directory exists.

        Args:
            `path` : The path to the file or directory to check.

        Returns:
            Result: A Result object containing a boolean in the data field indicating existence.

        Example:
            >>> result = file_manager.exists("some/file_or_directory")
            >>> if result.success:
            >>>     if result.data:
            >>>         print("Path exists!")
            >>>     else:
            >>>         print("Path does not exist.")
            >>> else:
            >>>     print(f"Existence check failed: {result.error_message}")
        """
        try:
            path = self._str_to_path(path)
            exists = path.exists()

            self._log("INFO", f"Existence check for {path}: {exists}")
            return Result(True, None, None, exists)
        except Exception as e:
            self._log("ERROR", f"Failed to check existence for {path}: {e}")
            return self._exception_tracker.get_exception_return(e)

    def exist(self, path: Union[str, Path]) -> Result:
        """
        Deprecated alias for `exists()`.
        """
        warnings.warn(
            "FileManager.exist() is deprecated; use FileManager.exists() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.exists(path)

    def delete_file(self, file_path: Union[str, Path]) -> Result:
        """
        Delete a file.

        - If the file does not exist, raise FileNotFoundError.

        Args:
            `file_path` : The path to the file to delete.

        Returns:
            Result: A Result object indicating success or failure of the delete operation.

        Example:
            >>> result = file_manager.delete_file("example.txt")
            >>> if result.success:
            >>>     print("File deleted successfully!")
            >>> else:
            >>>     print(f"File deletion failed: {result.error_message}")
        """
        try:
            file_path = self._str_to_path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            try:
                file_path.unlink()
            except PermissionError as e:
                self._log("ERROR", f"Permission denied when deleting {file_path}, attempting to change permissions and retry.")
                os.chmod(file_path, stat.S_IWRITE)
                file_path.unlink()

            self._log("INFO", f"Successfully deleted {file_path}")
            return Result(True, None, None, f"Successfully deleted {file_path}")
        except Exception as e:
            self._log("ERROR", f"Failed to delete {file_path}: {e}")
            return self._exception_tracker.get_exception_return(e)

    def delete_directory(self, dir_path: Union[str, Path]) -> Result:
        """
        Delete a directory and everything inside it.

        - If the directory does not exist, raise FileNotFoundError.

        Args:
            `dir_path` : The path to the directory to delete.

        Returns:
            Result: A Result object indicating success or failure of the delete operation.

        Example:
            >>> result = file_manager.delete_directory("some/directory")
            >>> if result.success:
            >>>     print("Directory deleted successfully!")
            >>> else:
            >>>     print(f"Directory deletion failed: {result.error_message}")
        """
        try:
            dir_path = self._str_to_path(dir_path)
            if not dir_path.exists():
                raise FileNotFoundError(f"Directory not found: {dir_path}")
            if not dir_path.is_dir():
                raise NotADirectoryError(f"Not a directory: {dir_path}")

            try:
                shutil.rmtree(dir_path)
            except PermissionError:
                self._log("ERROR", f"Permission denied when deleting {dir_path}, attempting to change permissions and retry.")
                try:
                    shutil.rmtree(dir_path, onexc=self._handle_exc)
                except TypeError:
                    shutil.rmtree(dir_path, onerror=self._handle_exc)

            self._log("INFO", f"Successfully deleted directory {dir_path}")
            return Result(True, None, None, f"Successfully deleted directory {dir_path}")
        except Exception as e:
            self._log("ERROR", f"Failed to delete directory {dir_path}: {e}")
            return self._exception_tracker.get_exception_return(e)

    def create_directory(self, dir_path: Union[str, Path]) -> Result:
        """
        Create a directory.

        - If the directory already exists, do nothing.

        Args:
            `dir_path` : The path to the directory to create.

        Returns:
            Result: A Result object indicating success or failure of the create operation.

        Example:
            >>> result = file_manager.create_directory("some/new/directory")
            >>> if result.success:
            >>>     print("Directory created successfully!")
            >>> else:
            >>>     print(f"Directory creation failed: {result.error_message}")
        """
        try:
            dir_path = self._str_to_path(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)

            self._log("INFO", f"Successfully created directory {dir_path}")
            return Result(True, None, None, f"Successfully created directory {dir_path}")
        except Exception as e:
            self._log("ERROR", f"Failed to create directory {dir_path}: {e}")
            return self._exception_tracker.get_exception_return(e)

    # __enter__ and __exit__
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
