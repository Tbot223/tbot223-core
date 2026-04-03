# external Modules
from multiprocessing import shared_memory, RLock, Lock
import pickle, json
from typing import Optional, Union
from pathlib import Path
import logging
import struct

# internal Modules
from tbot223_core.Result import Result
from tbot223_core.Exception import ExceptionTracker
from tbot223_core.LogSys import LoggerManager, Log

class GlobalVars:
    """
    Manage process-wide variables with optional shared-memory synchronization.

    `GlobalVars` supports three access styles:
    - explicit method calls such as `set()` and `get()`
    - attribute access such as `gv.api_key`
    - call syntax such as `gv("api_key", "value")`

    Shared-memory support is designed for trusted cooperating processes and
    includes lightweight ownership tracking:
    - `shm_gen()` creates the shared memory block when possible and records the
      current process as the owner.
    - If the requested name already exists, `shm_gen()` attaches to the
      existing block and verifies that the block is large enough.
    - Processes that only attach with `shm_connect()` should typically close
      their handle with `shm_close(name, close_only=True)`.
    - Cache eviction closes old handles but does not automatically unlink owned
      shared memory. Call `shm_close()` explicitly when cleanup matters.

    Example:
        >>> globals = GlobalVars()
        >>> globals.set("api_key", "12345", overwrite=True)
        >>> result = globals.get("api_key")
        >>> if result.success:
        >>>     print(result.data)  # Output: 12345
        >>> else:
        >>>     print(result.error)

        >>> # or using attribute access:

        >>> globals.api_key = "12345"
        >>> print(globals.api_key)  # Output: 12345

        >>> # or using call syntax:

        >>> globals("api_key", "12345", overwrite=True)
        >>> print(globals("api_key").data)  # Output: 12345

    Security:
    - Shared-memory methods such as `shm_sync()` and `shm_update()` support
      two serialization formats: `json` (default) and `pickle`.
    - `json` is the safer default, but it cannot serialize every Python object.
    - `pickle` can execute arbitrary code when deserializing untrusted data.
      Use it only when all participating processes are trusted.
    - For trusted processes that need pickle:
        >>> gv.shm_sync("my_shm", serialize_format="pickle")
        >>> gv.shm_update("my_shm", serialize_format="pickle")

    """

    _MISSING = object()

    def __init__(self, is_logging_enabled: bool=False, base_dir: Union[str, Path]=None,
                 shared_memory_cache_max_size: int=5,
                 logger_manager_instance: Optional[LoggerManager]=None, logger: Optional[logging.Logger]=None,
                 log_instance: Optional[Log]=None):

        # Set initialization flag to bypass __setattr__ during __init__
        object.__setattr__(self, '__initializing__', True)
        object.__setattr__(self, '__vars__', {})
        object.__setattr__(self, '__lock__', RLock())

        # Initialize Paths
        self._BASE_DIR = Path(base_dir) if base_dir is not None else Path.cwd()

        # Initialize Flags
        self.__is_logging_enabled__ = is_logging_enabled

        # Initialize Classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = None
        self._logger = None
        if self.__is_logging_enabled__:
            self._logger_manager = logger_manager_instance or LoggerManager(base_dir=self._BASE_DIR / "logs", second_log_dir="global_vars")
            self._logger_manager.make_logger("GlobalVarsLogger")
            self._logger = logger or self._logger_manager.get_logger("GlobalVarsLogger").data
        self.log = log_instance or Log(logger=self._logger)

        # Shared Memory Attributes
        self.__shm_name__ = set()
        self.__shm_owner__ = set()
        self.__shm_cache__ = {}
        self.__shm_cache_max_size__ = shared_memory_cache_max_size

        self.SERIALIZERS = {
            "pickle": (
                    lambda obj: pickle.dumps(obj),
                    lambda byte_data: pickle.loads(byte_data)
            ),
            "json": (
                    lambda obj: json.dumps(obj).encode('utf-8'),
                    lambda byte_data: json.loads(byte_data.decode('utf-8'))
            )
        }

        # Initialization complete
        object.__setattr__(self, '__initializing__', False)

    def _log(self, level: str, message: str) -> None:
        if self.__is_logging_enabled__:
            self.log.log_message(level, message)

    def set(self, key: str, value: object, overwrite: bool=False) -> Result:
        """
        Set a global variable.

        Args:
            `key` : The name of the global variable.
            `value` : The value to set.
            `overwrite` : If True, overwrite existing variable. Defaults to False.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> result = globals.set("api_key", "12345", overwrite=True)
            >>> if result.success:
            >>>     print(result.data)  # Output: Global variable 'api_key' set.
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                if key is None or not isinstance(key, str) or key.strip() == "":
                    raise ValueError("key must be a non-empty string.")
                # inline existence check to avoid extra lock/log overhead from exists()
                if key in self.__vars__ and not overwrite:
                    raise KeyError(f"Global variable '{key}' already exists.")

                self.__vars__[key] = value
                self._log("INFO", f"Global variable '{key}' set.")
                return Result(True, None, None, f"Global variable '{key}' set.")
        except Exception as e:
            self._log("ERROR", f"Failed to set global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def get(self, key: str) -> Result:
        """
        Get a global variable.

        Args:
            `key` : The name of the global variable.

        Returns:
            Result: A Result object containing the value of the global variable.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.get("api_key")
            >>> if result.success:
            >>>     print(result.data)  # Output: 12345
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                if key not in self.__vars__:
                    raise KeyError(f"Global variable '{key}' does not exist.")

                self._log("INFO", f"Global variable '{key}' accessed.")
                return Result(True, None, None, self.__vars__[key])
        except Exception as e:
            self._log("ERROR", f"Failed to get global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def delete(self, key: str) -> Result:
        """
        Delete a global variable.

        Args:
            `key` : The name of the global variable.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.delete("api_key")
            >>> if result.success and not globals.exists("api_key").data:
            >>>     print("api_key deleted successfully.")
            >>> else:
            >>>     print("Failed to delete api_key.")
        """
        try:
            with self.__lock__:
                if key not in self.__vars__:
                    raise KeyError(f"Global variable '{key}' does not exist.")

                del self.__vars__[key]
                self._log("INFO", f"Global variable '{key}' deleted.")
                return Result(True, None, None, f"Global variable '{key}' deleted.")
        except Exception as e:
            self._log("ERROR", f"Failed to delete global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def clear(self) -> Result:
        """
        Clear all global variables.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> globals.set("user_id", "user_01", overwrite=True)
            >>> result = globals.clear()
            >>> if result.success and len(globals.list_vars().data) == 0:
            >>>     print("All global variables cleared.")
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                self.__vars__.clear()

                self._log("INFO", "All global variables cleared.")
                return Result(True, None, None, "All global variables cleared.")
        except Exception as e:
            self._log("ERROR", f"Failed to clear global variables: {e}")
            return self._exception_tracker.get_exception_return(e)

    def list_vars(self) -> Result:
        """
        List all global variables.

        Returns:
            Result: A Result object containing a list of global variable names.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> globals.set("user_id", "user_01", overwrite=True)
            >>> result = globals.list_vars()
            >>> if result.success:
            >>>     print(result.data)  # Output: ['api_key', 'user_id']
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                self._log("INFO", "Listing all global variables.")
                return Result(True, None, None, list(self.__vars__.keys()))
        except Exception as e:
            self._log("ERROR", f"Failed to list global variables: {e}")
            return self._exception_tracker.get_exception_return(e)

    def exists(self, key: str) -> Result:
        """
        Check if a global variable exists.

        Args:
            `key` : The name of the global variable.

        Returns:
            Result: A Result object containing a boolean indicating existence.

        Example:
            >>> globals = GlobalVars()
            >>> globals.set("api_key", "12345", overwrite=True)
            >>> result = globals.exists("api_key")
            >>> if result.success:
            >>>     print(result.data)  # Output: True
            >>> else:
            >>>     print(result.error)
        """
        try:
            with self.__lock__:
                exists = key in self.__vars__
                self._log("INFO", f"Checked existence of global variable '{key}': {exists}")
                return Result(True, None, None, exists)
        except Exception as e:
            self._log("ERROR", f"Failed to check existence of global variable '{key}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def __getattr__(self, name: str) -> object:
        """
        Get a global variable by attribute access.

        Args:
            `name` : The name of the global variable.

        Returns:
            The value of the global variable.

        Example:
            >>> globals = GlobalVars()
            >>> globals.api_key = "12345"
            >>> print(globals.api_key)  # Output: 12345 ( this part uses __getattr__ )
        """
        try:
            with object.__getattribute__(self, '__lock__'):
                vars_dict = object.__getattribute__(self, '__vars__')
                if name not in vars_dict:
                    raise KeyError(name)
                return vars_dict[name]
        except KeyError as exc:
            raise AttributeError(f"'{type(self).__name__}' object has no variable '{name}'") from exc
        except Exception as e:
            try:
                if object.__getattribute__(self, '__is_logging_enabled__'):
                    object.__getattribute__(self, 'log').log_message("ERROR", f"Failed to access variable '{name}': {e}")
            except Exception:
                pass
            raise

    def __setattr__(self, name: str, value: object) -> Union[None, Result]:
        """
        Set a global variable by attribute access.

        Args:
            `name` : The name of the global variable.
            `value` : The value to set.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> globals = GlobalVars()
            >>> globals.api_key = "12345" ( this part uses __setattr__ )
            >>> print(globals.api_key)  # Output: 12345
        """
        # During initialization, use normal attribute setting
        try:
            if object.__getattribute__(self, '__initializing__'):
                object.__setattr__(self, name, value)
                return
        except AttributeError:
            # __initializing__ not set yet, must be during early init
            object.__setattr__(self, name, value)
            return

        # After initialization, store in __vars__ dict
        try:
            with object.__getattribute__(self, '__lock__'):
                if name is None or not isinstance(name, str) or name.strip() == "":
                    raise ValueError("name must be a non-empty string.")

                vars_dict = object.__getattribute__(self, '__vars__')
                vars_dict[name] = value
                if object.__getattribute__(self, '__is_logging_enabled__'):
                    object.__getattribute__(self, 'log').log_message("INFO", f"Global variable '{name}' set via attribute access.")
        except Exception as e:
            exception_tracker = object.__getattribute__(self, '_exception_tracker')
            return exception_tracker.get_exception_return(e)

    def __call__(self, key: str, value: object=_MISSING, overwrite: bool=False) -> Result:
        """
        Get or set a global variable using call syntax.
        If value is provided, set the variable; otherwise, get it.

        Args:
            `key` : The name of the global variable.
            `value` : The value to set. If omitted, this method performs a get operation.
                `None` is treated as a valid value and will be stored.
            `overwrite` : If True, overwrite existing variable when setting. Defaults to False.

        Returns:
            Result: A Result object containing the value when getting, or indicating success/failure when setting

        Example:
            >>> globals = GlobalVars()
            >>> globals("api_key", "12345", overwrite=True)  # Set api_key
            >>> result = globals("api_key")  # Get api_key
            >>> if result.success:
            >>>     print(result.data)  # Output: 12345
            >>> else:
            >>>     print(result.error)
        """
        try:
            if value is not self._MISSING:
                return self.set(key, value, overwrite)
            else:
                return self.get(key)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)

    def shm_cache_management(self, name: Optional[str], shm: Optional[shared_memory.SharedMemory]) -> Result:
        """
        Maintain the internal shared-memory handle cache.

        This helper stores active `SharedMemory` handles, refreshes access
        order, and evicts the oldest cached handle when the cache limit is
        reached. Eviction closes the handle but does not automatically unlink
        the shared memory block.

        Args:
            `name` : Shared memory name, or `None` when clearing the cache.
            `shm` : Shared memory handle to cache, or `None`.
                - If both `name` and `shm` are provided, the cache entry is
                  added or refreshed.
                - If both are `None`, all cached handles are closed and the
                  cache is cleared.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> gv = GlobalVars()
            >>> shm = shared_memory.SharedMemory(name="my_shm")
            >>> gv.shm_cache_management("my_shm", shm)
        """
        try:
            if name is not None and not isinstance(name, str):
                raise ValueError("name must be a string or None")
            if shm is not None and not isinstance(shm, shared_memory.SharedMemory):
                raise ValueError("shm must be a shared_memory.SharedMemory object or None")
            with self.__lock__:
                should_add_new = name is not None and shm is not None and name not in self.__shm_cache__
                if should_add_new and len(self.__shm_cache__) >= self.__shm_cache_max_size__:
                    oldest_key = next(iter(self.__shm_cache__))
                    oldest_shm = self.__shm_cache__.pop(oldest_key)
                    oldest_shm.close()
                    if oldest_key in self.__shm_owner__:
                        self._log(
                            "WARNING",
                            f"Shared memory '{oldest_key}' evicted from cache. "
                            "Call shm_close() explicitly to unlink if this process is the owner."
                        )
                    else:
                        self._log("INFO", f"Shared memory cache for '{oldest_key}' removed due to cache size limit.")

                if name not in self.__shm_cache__ and shm is not None:
                    self.__shm_cache__[name] = shm
                    self._log("INFO", f"Shared memory cache for '{name}' created.")
                elif name in self.__shm_cache__ and shm is not None:
                    self.__shm_cache__[name] = shm
                    self._log("INFO", f"Shared memory cache for '{name}' updated.")
                elif name is None and shm is None:
                    for cached_shm in self.__shm_cache__.values():
                        cached_shm.close()
                    self.__shm_cache__.clear()
                    self._log("INFO", "All shared memory caches cleared.")
                else:
                    shm_obj = self.__shm_cache__.get(name)
                    self.__shm_cache__.pop(name, None)
                    self.__shm_cache__[name] = shm_obj
                    self._log("INFO", f"Shared memory cache for '{name}' accessed.")

            return Result(True, None, None, "success to manage shared memory cache")
        except Exception as e:
            self._log("ERROR", f"Failed to manage shared memory cache: {e}")
            return self._exception_tracker.get_exception_return(e)

    def shm_gen(self, name: str=None, size: int=1024, create_lock: bool=True) -> Result:
        """
        Create or attach to a shared-memory block for inter-process use.

        When the named block does not exist, this method creates it and marks
        the current process as the owner. If the name already exists, the
        method attaches to the existing block instead and verifies that the
        block is large enough for the requested size.

        Args:
            `name` : Shared memory name.
            `size` : Requested size in bytes.
            `create_lock` : If `True`, also create a `multiprocessing.Lock`
                for cross-process synchronization.

        Returns:
            Result: A Result object.
            - If `create_lock` is `False`, `data` contains a success message.
            - If `create_lock` is `True`, `data` contains the generated lock.

        Example:
            >>> gv.shm_gen("my_shm", size=4096)
            >>> result = gv.shm_gen("my_shm", size=4096, create_lock=True)
            >>> shm_lock = result.data
        """
        try:
            if name is None or not isinstance(name, str) or name.strip() == "":
                raise ValueError("name must be a non-empty string.")
            if not isinstance(size, int) or size <= 0:
                raise ValueError("size must be a positive integer.")

            try:
                shm = shared_memory.SharedMemory(create=True, size=size, name=name)
                self.__shm_owner__.add(name)
            except FileExistsError:
                self._log("WARNING", f"Shared memory '{name}' already exists. Connecting to existing one.")
                shm = shared_memory.SharedMemory(name=name)
                if shm.size < size:
                    shm.close()
                    raise ValueError(f"Existing SHM '{name}' size ({shm.size}) < requested ({size})")
            self.__shm_name__.add(name)
            self.shm_cache_management(name, shm)  # Keep reference to prevent GC
            self._log("INFO", f"Shared memory object '{shm.name}' created.")

            if create_lock:
                lock = Lock()
                return Result(True, None, None, lock)
            return Result(True, None, None, "success to create shared memory object")
        except Exception as e:
            self._log("ERROR", f"Failed to create shared memory object: {e}")
            return self._exception_tracker.get_exception_return(e)

    def shm_connect(self, name: str) -> Result:
        """
        Attach to an existing shared-memory block without creating ownership.

        This method is intended for child or worker processes. Unlike
        `shm_gen()`, it never creates a new block and does not record the
        current process as the owner.

        Args:
            `name` : Shared memory name.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> # In main process:
            >>> gv_main = GlobalVars()
            >>> result = gv_main.shm_gen("my_shm", size=4096, create_lock=True)
            >>> shm_lock = result.data
            >>>
            >>> # In child process:
            >>> gv_child = GlobalVars()
            >>> gv_child.shm_connect("my_shm")
            >>> with shm_lock:
            >>>     gv_child.shm_update("my_shm")
            >>>     # ... modify ...
            >>>     gv_child.shm_sync("my_shm")
        """
        try:
            res = self.shm_get(name)
            if not res.success:
                return res

            if name not in self.__shm_name__:
                self.__shm_name__.add(name)

            self._log("INFO", f"Connected to shared memory object '{name}'.")
            return Result(True, None, None, f"Connected to shared memory object '{name}'.")
        except FileNotFoundError:
            self._log("ERROR", f"Shared memory object '{name}' does not exist.")
            return Result(False, "FileNotFoundError", f"Shared memory object '{name}' does not exist.", None)
        except Exception as e:
            self._log("ERROR", f"Failed to connect to shared memory object '{name}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def shm_get(self, name: str) -> Result:
        """
        Return a cached shared-memory handle, or attach to it if needed.

        Args:
            `name` : Shared memory name.

        Returns:
            Result: A Result object containing the `SharedMemory` handle.

        Example:
            >>> gv = GlobalVars()
            >>> gv.shm_gen("my_shm", size=4096)
            >>> shm = gv.shm_get("my_shm").data
            >>> print(shm.name)  # Output: my_shm
        """
        try:
            if name not in self.__shm_cache__:
                self._log("WARNING", f"Shared memory object '{name}' not found in cache.")
                shm = shared_memory.SharedMemory(name=name)
                self.shm_cache_management(name, shm)
                self._log("INFO", f"Shared memory object '{name}' created and added to cache.")
                return Result(True, None, None, shm)
            shm = self.__shm_cache__[name]
            self._log("INFO", f"Shared memory object '{name}' retrieved from cache.")
            return Result(True, None, None, shm)
        except Exception as e:
            self._log("ERROR", f"Failed to retrieve shared memory object '{name}' from cache: {e}")
            return self._exception_tracker.get_exception_return(e)

    def shm_sync(self, name: str, serialize_format: str="json") -> Result:
        """
        Serialize the current variables and write them into shared memory.

        Supported formats:
        - `json` (default): safer, but limited to JSON-serializable values
        - `pickle`: more flexible, but unsafe for untrusted data

        Args:
            `name` : Shared memory name.
            `serialize_format` : Serialization format. Must be `"json"` or
                `"pickle"`.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> gv = GlobalVars()
            >>> gv.shm_gen("my_shm", size=4096)
            >>> gv.some_variable = 42
            >>> gv.shm_sync("my_shm")
            >>> # In another process:
            >>> gv.shm_update("my_shm")
            >>> print(gv.some_variable)  # Output: 42
        """
        try:
            if serialize_format not in self.SERIALIZERS:
                raise ValueError(f"Unsupported serialization format: {serialize_format}")

            byte_dict = self.SERIALIZERS[serialize_format][0](self.__vars__)

            data_len = len(byte_dict)
            header_size = 8 # bytes to store length of data

            if name not in self.__shm_name__:
                raise ValueError("Shared memory name does not match the created one.")
            if name not in self.__shm_cache__:
                shm = shared_memory.SharedMemory(name=name)
                self.shm_cache_management(name, shm)
            else:
                shm = self.__shm_cache__[name]

            if data_len + header_size > shm.size:
                raise MemoryError(f"Serialized data size ({data_len + header_size} bytes) exceeds shared memory size ({shm.size} bytes).")

            shm.buf[:header_size] = struct.pack('Q', data_len)
            shm.buf[header_size:header_size+data_len] = byte_dict

            self._log("INFO", f"Shared memory object '{name}' synchronized.")
            return Result(True, None, None, "success to synchronize shared memory object")
        except Exception as e:
            self._log("ERROR", f"Failed to synchronize shared memory object '{name}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def shm_update(self, name: str, serialize_format: str="json") -> Result:
        """
        Read serialized data from shared memory and merge it into this object.

        Use the same `serialize_format` that was used with `shm_sync()`.

        Args:
            `name` : Shared memory name.
            `serialize_format` : Serialization format. Must match the format
                used when the data was written.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> gv = GlobalVars()
            >>> gv.shm_gen("my_shm", size=4096)
            >>> gv.some_variable = 42
            >>> gv.shm_sync("my_shm")
            >>> # In another process:
            >>> gv.shm_update("my_shm")
            >>> print(gv.some_variable)  # Output: 42
        """
        try:
            if serialize_format not in self.SERIALIZERS:
                raise ValueError(f"Unsupported serialization format: {serialize_format}")

            shm = self.shm_get(name).data
            header_size = 8 # bytes to store length of data

            packed_len = bytes(shm.buf[:header_size])
            (data_len,) = struct.unpack('Q', packed_len)

            if data_len == 0:
                self._log("WARNING", f"No data found in shared memory object '{name}'.")
                return Result(True, None, None, "no data to update from shared memory object")

            byte_dict = bytes(shm.buf[header_size:header_size+data_len])

            try:
                obj_dict = self.SERIALIZERS[serialize_format][1](byte_dict)
            except Exception as e:
                raise ValueError(f"Deserialization error ({serialize_format}). Read {data_len} bytes from shared memory but failed to deserialize: {e}")

            with self.__lock__:
                self.__vars__.update(obj_dict)

            self._log("INFO", f"Shared memory object '{name}' updated.")
            return Result(True, None, None, "success to update from shared memory object")
        except Exception as e:
            self._log("ERROR", f"Failed to update from shared memory object '{name}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def shm_close(self, name: str, close_only: bool = False) -> Result:
        """
        Close a shared-memory handle and optionally unlink the block.

        Ownership matters:
        - The owner process can call `shm_close(name)` to close and unlink.
        - Non-owner processes should usually call
          `shm_close(name, close_only=True)`.
        - If a non-owner calls `shm_close(name)` without `close_only=True`,
          the handle is closed but the block is not unlinked.

        Args:
            `name` : Shared memory name.
            `close_only` : If `True`, close only the local handle.

        Returns:
            Result: A Result object indicating success or failure.

        Example:
            >>> gv = GlobalVars()
            >>> gv.shm_gen("my_shm", size=4096)
            >>> gv.shm_close("my_shm")
        """
        try:
            if name not in self.__shm_name__:
                raise ValueError("Shared memory name does not match the created one.")
            shm = self.shm_get(name).data
            shm.close()
            if not close_only and name in self.__shm_owner__:
                shm.unlink()
                self.__shm_name__.discard(name)
                self.__shm_owner__.discard(name)
                self._log("INFO", f"Shared memory object '{name}' closed and unlinked.")
            elif not close_only:
                self.__shm_name__.discard(name)
                self._log("WARNING", f"Shared memory object '{name}' closed without unlink because this process is not the owner.")
            else:
                self._log("INFO", f"Shared memory object '{name}' closed.")
            self.__shm_cache__.pop(name, None)

            return Result(True, None, None, "success to close shared memory object")
        except Exception as e:
            self._log("ERROR", f"Failed to close shared memory object '{name}': {e}")
            return self._exception_tracker.get_exception_return(e)

    def lock(self) -> RLock: # type: ignore
        """
        Return the `RLock` used to guard this instance's state.

        Returns:
            multiprocessing.RLock: The RLock object.
            This method intentionally returns the lock directly instead of using
            the `Result` wrapper.

        Example:
            >>> gv = GlobalVars()
            >>> with gv.lock():
            >>>     gv.set("counter", gv.get("counter").data + 1, overwrite=True)
            >>>     # Critical section to safely modify 'counter'
        """
        return self.__lock__

    def __enter__(self):
        self.__lock__.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__lock__.release()
