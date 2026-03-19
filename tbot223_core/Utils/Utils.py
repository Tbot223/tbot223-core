# external Modules
import hashlib, secrets
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# internal Modules
from tbot223_core.Exception import ExceptionTracker
from tbot223_core.LogSys import LoggerManager, Log
from tbot223_core.Result import Result

class Utils:
    """
    Utility class providing various helper functions.

    Methods:
        - str_to_path(path_str) -> Result
            Convert a string to a Path object.
        
        - hashing(data, algorithm) -> Result
            Hash a string using the specified algorithm.

        - pbkdf2_hmac(password, algorithm, iterations, salt_size) -> Result
            Generate a PBKDF2 HMAC hash of the given password.

        - verify_pbkdf2_hmac(password, salt_hex, hash_hex, iterations, algorithm) -> Result
            Verify a PBKDF2 HMAC hash of the given password.

        - insert_at_intervals(data, interval, insert, at_start) -> Result
            Insert a specified element into a list or string at regular intervals.

        - find_keys_by_value(dict_obj, threshold, comparison, nested) -> Result
            Find keys in a dictionary based on value comparisons.
    """
    
    def __init__(self, is_logging_enabled: bool=False,
                 base_dir: Union[str, Path]=None,
                 logger_manager_instance: Optional[LoggerManager]=None, logger: Optional[logging.Logger]=None, 
                 log_instance: Optional[Log]=None):
        """
        Initialize Utils class.
        """
        # Initialize Paths
        self._BASE_DIR = Path(base_dir or Path.cwd())

        # Initialize Flags
        object.__setattr__(self, '__is_logging_enabled__', is_logging_enabled)

        # Initialize Classes
        self._exception_tracker = ExceptionTracker()
        self._logger_manager = None
        self._logger = None
        if self.__is_logging_enabled__:
            self._logger_manager = logger_manager_instance or LoggerManager(base_dir=self._BASE_DIR / "logs", second_log_dir="utils")
            self._logger_manager.make_logger("UtilsLogger")
            self._logger = logger or self._logger_manager.get_logger("UtilsLogger").data
        self.log = log_instance or Log(logger=self._logger)

        if self.__is_logging_enabled__:
            self.log.log_message("INFO", "Utils initialized.")

    # Internal Methods
    def _check_pbkdf2_params(self, password: str, algorithm: str, iterations: int, salt_size: int = 32) -> None:
        """
        Check parameters for PBKDF2 HMAC functions.

        Args:
            - password : The password string.
            - algorithm : The hashing algorithm to use.
            - iterations : Number of iterations.
            - salt_size : Size of the salt in bytes (default: 32).

        Raises:
            ValueError: If any parameter is invalid.
        
        Example:
            >>> I'm Not recommending to call this method directly, It's for internal use.
            >>> utils = Utils()
            >>> utils._check_pdkdf2_params("my_password", "sha256", 100000, 32)
            >>> # No exception raised for valid parameters.
        """
        if not isinstance(password, str):
            raise ValueError("password must be a string")
        if algorithm not in ['sha1', 'sha256', 'sha512']:
            raise ValueError("Unsupported algorithm. Supported algorithms: 'sha1', 'sha256', 'sha512'")
        if not isinstance(iterations, int) or iterations <= 0:
            raise ValueError("iterations must be a positive integer")
        if not isinstance(salt_size, int) or salt_size <= 0:
            raise ValueError("salt_size must be a positive integer")
        
    def _lookup_dict(self, dict_obj: Dict, threshold: Union[int, float, str, bool], comparison_func: Callable, comparison_type: str, nested: bool = False, separator: str = "/" , return_mod: str = "flat", prefix_marker: str = "") -> Union[List[Union[str, Dict]], Tuple[Union[str, Dict], ...]]:
        """
        Helper method to recursively look up keys in a dictionary based on a comparison function.

        Args:
            dict_obj : The dictionary to search.
            threshold : The value to compare against.
            comparison_func : A callable that takes a value and returns True if it meets the condition.
            comparison_type : The type of comparison being performed.
            nested : If True, search within nested dictionaries.
            separator : A string to prefix nested keys with. Defaults to "/". (If "tuple", returns tuple, if "list", returns list)
            return_mod : The mode of return format.
                - "flat": Return a list of keys only. If nested, don't include parent keys. DO NOT USE FOR NESTED KEYS.
                - "forest": Return a list of dicts with key-value pairs.
                - "path": Returns a list of full paths with separators
            prefix_marker : DO NOT USE, for internal use only to mark nested keys.

        Returns:
            A list of keys that meet the comparison criteria.

        Example:
            >>> # I'm not recommending to call this method directly, it's for internal use.
            >>> my_dict = {'a': 10, 'b': 20, 'c': 30}
            >>> found_keys = app_core._lookup_dict(my_dict, threshold=20, comparison_func=lambda x: x > 20, comparison_type='gt', nested=False)
            >>> print(found_keys)  # Output: ['c']
        """
        found_keys = []
        for key, value in dict_obj.items():
            if isinstance(value, (tuple, list)):
                if self.__is_logging_enabled__:
                    self.log.log_message("DEBUG", f"Skipping iterable at key '{key}'.")
                continue
            if nested and isinstance(value, dict):
                if self.__is_logging_enabled__:
                    self.log.log_message("DEBUG", f"Searching nested dictionary at key '{key}'.")
                if return_mod == "flat":
                    found_keys.append(self._lookup_dict(value, threshold, comparison_func, comparison_type, nested, separator, "flat"))
                elif return_mod == "forest":
                    found_keys.append({key: self._lookup_dict(value, threshold, comparison_func, comparison_type, nested, separator, "forest")})
                elif return_mod == "path":
                    found_keys.extend(self._lookup_dict(value, threshold, comparison_func, comparison_type, nested, separator, "path", f"{prefix_marker}{key}{separator}"))
            elif type(value) is not type(threshold) and comparison_type in ('eq', 'ne'):
                if self.__is_logging_enabled__:
                    self.log.log_message("DEBUG", f"Type mismatch at key '{key}': {type(value).__name__} vs {type(threshold).__name__}. Skipping.")
                continue
            else:
                if comparison_func(value):
                    if return_mod == "flat":
                        found_keys.append(key)
                    elif return_mod == "forest":
                        found_keys.extend({key: value})
                    elif return_mod == "path":
                        found_keys.append(f"{prefix_marker}{key}")

                    if self.__is_logging_enabled__:
                        self.log.log_message("DEBUG", f"Key '{prefix_marker}{key}' matches the condition.")
        return tuple(found_keys) if separator == "tuple" else found_keys

    # external Methods
    def str_to_path(self, path_str: str) -> Path:
        """
        Convert a string to a Path object.

        Args:
            - path_str : The string representation of the path.
            
        Returns:
            Result: A Result object containing the Path object.
        
        Example:
            >>> result = utils.str_to_path("/home/user/documents")
            >>> if result.success:
            >>>     path = result.data # Path object
            >>>     print(path.exists())
            >>> else:
            >>>     print(result.error)
        """
        try:
            if not isinstance(path_str, str):
                return Result(True, None, None, path_str)

            return Result(True, None, None, Path(path_str))
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
        
    def hashing(self, data: str, algorithm: str='sha256') -> Result:
        """
        Encrypt a string using the specified algorithm.
        Supported algorithms: 'md5', 'sha1', 'sha256', 'sha512'

        **WARNING**: 
            - Hashing is not encryption. Hashing is a one-way function and cannot be reversed.
            - md5 and sha1 are considered weak and not recommended for security-sensitive applications.

        Args:
            - data : The string to encrypt.
            - algorithm : The hashing algorithm to use. Defaults to 'sha256'

        Returns:
            Result: A Result object containing the encrypted string in hexadecimal format.

        Example:
            >>> result = utils.encrypt("my_secret_data", algorithm='sha256')
            >>> if result.success:
            >>>     encrypted_data = result.data
            >>>     print(encrypted_data)
            >>> else:
            >>>     print(result.error)
        """
        try:
            if not isinstance(data, str):
                raise ValueError("data must be a string")
            if algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:
                raise ValueError("Unsupported algorithm. Supported algorithms: 'md5', 'sha1', 'sha256', 'sha512'")

            hash_func = getattr(hashlib, algorithm)()
            hash_func.update(data.encode('utf-8'))
            encrypted_data = hash_func.hexdigest()

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"Data encrypted using {algorithm}.")
            return Result(True, None, None, encrypted_data)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Encryption failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def pbkdf2_hmac(self, password: str, algorithm: str, iterations: int, salt_size: int) -> Result:
        """
        Generate a PBKDF2 HMAC hash of the given password.
        Supported algorithms: 'sha1', 'sha256', 'sha512'

        This function returns a dict containing the salt (hex), hash (hex), iterations, and algorithm used.

        Args:
            - password : The password string.
            - algorithm : The hashing algorithm to use.
            - iterations : Number of iterations.
            - salt_size : Size of the salt in bytes.

        Returns:
            Result: A Result object containing a dict with the following keys:
        
        Example:
            >>> result = utils.pbkdf2_hmac("my_password", "sha256", 100000, 32)
            >>> if result.success:
            >>>     hash_info = result.data
            >>>     print(hash_info)
            >>> else:
            >>>     print(result.error)
        """
        try:
            self._check_pbkdf2_params(password, algorithm, iterations, salt_size)
            
            salt = secrets.token_bytes(salt_size)
            hash_bytes = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)

            salt_hex = salt.hex()
            hash_hex = hash_bytes.hex()
            result = {
                "salt_hex": salt_hex,
                "hash_hex": hash_hex,
                "iterations": iterations,
                "algorithm": algorithm
            }

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"PBKDF2 HMAC hash generated using {algorithm} with {iterations} iterations.")
            return Result(True, None, None, result)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"PBKDF2 HMAC hash generation failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def verify_pbkdf2_hmac(self, password: str, salt_hex: str, hash_hex: str, iterations: int, algorithm: str) -> Result:
        """
        Verify a PBKDF2 HMAC hash of the given password.
        Supported algorithms: 'sha1', 'sha256', 'sha512'

        This function returns True if the password matches the hash, False otherwise.

        Args:
            - password : The password string to verify.
            - salt_hex : The salt in hexadecimal format.
            - hash_hex : The hash in hexadecimal format.
            - iterations : Number of iterations.
            - algorithm : The hashing algorithm to use.

        Returns:
            Result: A Result object containing a boolean indicating whether the password matches the hash.

        Example:
            >>> hash_info = {
            >>>     "salt_hex": "a1b2c3d4e5f6...",
            >>>     "hash_hex": "abcdef123456...",
            >>>     "iterations": 100000,
            >>>     "algorithm": "sha256"
            >>> }
            >>> result = utils.verify_pbkdf2_hmac("my_password", hash_info["salt_hex"], hash_info["hash_hex"], hash_info["iterations"], hash_info["algorithm"])
            >>> if result.success:
            >>>     is_valid = result.data
            >>>     print(is_valid)  # True or False
            >>> else:
            >>>     print(result.error)
        """
        try:
            self._check_pbkdf2_params(password, algorithm, iterations)
            if not isinstance(salt_hex, str) or not isinstance(hash_hex, str):
                raise ValueError("salt_hex and hash_hex must be strings")
            
            salt = bytes.fromhex(salt_hex)
            excepted_hash = bytes.fromhex(hash_hex)
            hash_bytes = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)

            is_valid = secrets.compare_digest(hash_bytes, excepted_hash)
            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"PBKDF2 HMAC hash verification using {algorithm} with {iterations} iterations. Result: {is_valid}")
            return Result(True, None, None, is_valid)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"PBKDF2 HMAC hash verification failed: {e}")
            return self._exception_tracker.get_exception_return(e)
        
    def insert_at_intervals(self, data: Union[List, str], interval: int, insert: Any, at_start: bool=True) -> Result:
        """
        Insert a specified element into a list or string at regular intervals.

        Args:
            - data : The original list or string where elements will be inserted.
            - interval : The interval at which to insert the element. (must be a positive integer)
            - insert : The element to insert into the list or string. (if data is a string, using object like callable is not recommended as it will be converted to string)
            - at_start : If True, insertion starts at the beginning (index 0). If False, insertion starts after the first interval. Defaults to True.

        Returns:
            Result: A Result object containing the modified list or string.

        Example:
            >>> utils = Utils()
            >>> data_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            >>> result = utils.insert_at_intervals(data_list, 3, 'X', at_start=True)
            >>> if result.success:
            >>>    print(result.data)  # Output: ['X', 1, 2, 3, 'X', 4, 5, 6, 'X', 7, 8, 9]
            >>> else:
            >>>    print(result.error)
        """
        try:
            if not isinstance(data, (list, str)):
                raise ValueError("data must be a list or string")
            if not isinstance(interval, int) or interval <= 0:
                raise ValueError("interval must be a positive integer")
            if not isinstance(at_start, bool):
                raise ValueError("at_start must be a boolean value")
        
            original_type_is_str = False
            if isinstance(data, str):
                original_type_is_str = True
                data = list(data)

            # Build new list by inserting at intervals (iterate in reverse to avoid index shifting issues)
            result_data = list(data)
            start_index = 0 if at_start else interval
            insert_count = 0
            
            # Calculate positions from the end to maintain correct indices
            positions_to_insert = list(range(start_index, len(result_data) + insert_count * (interval + 1), interval + 1))
            
            # Insert in reverse order to avoid index shifting
            for pos in reversed(positions_to_insert):
                if pos <= len(result_data):
                    result_data.insert(pos, insert)
                    insert_count += 1

            if original_type_is_str:
                result_data = ''.join(map(str, result_data))
            return Result(True, None, None, result_data)
        except Exception as e:
            return self._exception_tracker.get_exception_return(e)
    
    def find_keys_by_value(self, dict_obj: Dict, threshold: Union[int, float, str, bool],  comparison: str='eq', nested: bool=False, separator: str = "/", return_mod: str = "flat") -> Result:
        """
        Find keys in dict_obj where their values meet the threshold based on the comparison operator.

        [bool, str] - [int, float] comparisons are only supported for 'eq' and 'ne'.

        Args:
            dict_obj : The dictionary to search.
            threshold : The value to compare against.
            comparison : The comparison operator as a string. Default is 'eq' (equal).
            nested : If True, search within nested dictionaries.
            separator : The string to prepend to keys for nested dictionaries (default: "/"). ( If "tuple", returns tuple, if "list", returns list )
            return_mod : The mode of return format.
                - **"flat"**: Return a list of keys only.
                - **"forest"**: Return a list of dicts with key-value pairs.
                - **"path"**: Returns a list of full paths with separators

        Returns:
            A list of keys that meet the comparison criteria.

        Example:
            >>> my_dict = {'a': 10, 'b': 20, 'c': 30}
            >>> result = app_core.find_keys_by_value(my_dict, threshold=20, comparison='gt', nested=False)
            >>> print(result.data)  # Output: ['c']

        Supported comparison operators:
        - 'eq': equal to
        - 'ne': not equal to
        - 'lt': less than
        - 'le': less than or equal to
        - 'gt': greater than
        - 'ge': greater than or equal to
        """
        comparison_operators = {
            'eq': lambda x: x == threshold,
            'ne': lambda x: x != threshold,
            'lt': lambda x: x < threshold,
            'le': lambda x: x <= threshold,
            'gt': lambda x: x > threshold,
            'ge': lambda x: x >= threshold,
        }

        try:
            if comparison not in comparison_operators:
                raise ValueError(f"Unsupported comparison operator: {comparison}")
            if isinstance(dict_obj, dict) is False:
                raise ValueError("Input data must be a dictionary")
            if isinstance(threshold, (str, bool, int, float)) is False:
                raise ValueError("Threshold must be of type str, bool, int, or float")
            if not isinstance(nested, bool):
                raise ValueError("nested must be a boolean value")
            if not isinstance(separator, str):
                raise ValueError("separator must be a string")
            if return_mod not in ("flat", "forest", "path"):
                raise ValueError("return_mod must be one of 'flat', 'forest', or 'path'")
            if return_mod == "path" and separator in ("list", "tuple"):
                raise ValueError("separator cannot be 'list' or 'tuple' when return_mod is 'path'")
            
            comparison_func = comparison_operators[comparison]
            found_keys = self._lookup_dict(dict_obj, threshold, comparison_func, comparison, nested, separator=separator, return_mod=return_mod)

            if self.__is_logging_enabled__:
                self.log.log_message("INFO", f"find_keys_by_value found {len(found_keys)} keys matching criteria.")
            return Result(True, None, None, found_keys)
        except Exception as e:
            if self.__is_logging_enabled__:
                self.log.log_message("ERROR", f"Error in find_keys_by_value: {str(e)}")
            return self._exception_tracker.get_exception_return(e)