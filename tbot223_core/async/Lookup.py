# external Modules
import secrets
from typing import Any, AsyncGenerator, Callable, Tuple, Union

# internal Modules
from tbot223_core.Result import Result
from tbot223_core._default_init import DefaultInit

class LookupDictHelper:
    @staticmethod
    def _secure_random_string(count: int, length: int = 16) -> list[str]:
        """
        Generates a list of unique random strings using the secrets module.

        Args:
            count (int): The number of unique random strings to generate.
            length (int): The length of each random string (default is 16).

        Returns:
            list[str]: A list containing the generated unique random strings.


        """
        generated_ids = set()
        result = []
        for _ in range(count):
            while True:
                tmp = secrets.token_hex(length)
                if tmp not in generated_ids:
                    break
            generated_ids.add(tmp)
            result.append(tmp)
        return result

    @staticmethod
    def _safety_check(dictionary: dict, comparator: Callable[[Any], bool]) -> bool:
        """
        Checks if the provided dictionary and comparator are valid for the lookup operations.

        Args:
            dictionary (dict): The dictionary to be checked.
            comparator (Callable[[Any], bool]): The comparator function to be checked.
        """
        if not isinstance(dictionary, dict):
            raise ValueError("The provided dictionary is not a valid dictionary.")
        if not callable(comparator):
            raise ValueError(
                "The provided comparator is not a valid callable function."
            )
        return True

    @staticmethod
    def _consistency_check(origin: Union[list, Tuple], new: Union[list, Tuple]) -> bool:
        for o, n in zip(origin, new):
            if type(o) is not type(n):
                return False
            if o != n:
                return False
        return True

    @staticmethod
    def _get_comparator_by_key(comparison: str):
        pass

    @staticmethod
    def _get_comparator_by_value(comparison: str):
        pass

class LookupDict(LookupDictHelper):
    def __init__(self, is_logging_enabled: bool = False, is_debug_enabled: bool = False):
        """
        Initializes the LookupDict instance.

        Args:
            is_logging_enabled (bool): Whether logging is enabled.
            is_debug_enabled (bool): Whether debug mode is enabled.

        Returns:
            None
        """
        DefaultInit.run(self, is_logging_enabled, is_debug_enabled)

    # interal Methods
    @staticmethod
    async def _generic_finder_generator(
        dictionary: dict,
        comparator: Callable[[Any], bool],
        nested: bool = False,
        separator: str = "//",
        safety: Tuple[bool, bool] = (False, False),
        path_prefix: str = "",
        identifier: str = "",
        depth: int = 0,
        target: str = "VALUE",
    ) -> AsyncGenerator[Tuple[Any, Any, str, int], None]:
        """
        Core async generator that performs the lookup operation. Yields results as they are found.

        Args:
            dictionary (dict): The dictionary to search through.
            comparator (Callable[[Any], bool]): A function that takes a key or value and returns True if it matches the search criteria.
            nested (bool): Whether to search through nested dictionaries (default is False).
            separator (str): The string used to separate keys in the path (default is '//').
            safety (Tuple[bool, bool]): A tuple where the first element enables hyper-safe mode (ensuring all keys are found) and the second element enables hyper-consistent mode (ensuring consistent results across iterations). Default is (False, False).
            path_prefix (str): A prefix to be added to the path of found items (used for nested searches, default is '').
            identifier (str): An optional identifier for error messages in hyper-safe mode (default is '').
            depth (int): The current depth of the search (used for nested searches, default is 0).
            target (str): Determines whether the comparator is applied to keys ('KEY') or values ('VALUE'). Default is 'VALUE'.
        """
        key_to_find = dict()
        keys = dictionary.keys()
        ids = LookupDictHelper._secure_random_string(len(keys), 16)

        if safety[0]:
            for key, id_val in zip(keys, ids):
                key_to_find[key] = f"<NOT FOUND VALUE. identifier={id_val}>"

        for key, value in dictionary.items():
            is_nested_dict = nested and isinstance(value, dict)

            if is_nested_dict:
                async for item in LookupDict._generic_finder_generator(
                    dictionary=value,
                    comparator=comparator,
                    nested=nested,
                    separator=separator,
                    safety=safety,
                    path_prefix=path_prefix + key + separator,
                    identifier=identifier,
                    depth=depth + 1,
                    target=target,
                ):
                    yield item
                if safety[0]:
                    key_to_find[key] = None

            matched = (target == "KEY" and comparator(key)) or (
                target == "VALUE" and not is_nested_dict and comparator(value)
            )

            if matched:
                yield (key, value, path_prefix + key, depth)
                if safety[0]:
                    key_to_find[key] = None

        if safety[0]:
            for key, value in key_to_find.items():
                if value is not None:
                    raise ValueError(
                        f"Value for key '{key}' was not found. Identifier: {value}"
                    )

    @staticmethod
    async def _generic_finder(
        dictionary: dict,
        comparator: Callable[[Any], bool],
        nested: bool = False,
        return_mode: str = "PATH",
        separator: str = "//",
        safety: Tuple[bool, bool] = (False, False),
        path_prefix: str = "",
        identifier: str = "",
        target: str = "VALUE",
    ) -> Union[list, Tuple, AsyncGenerator[Tuple[Any, Any, str, int], None]]:
        """
        Core async function that performs the lookup operation. Collects results into a list based on the specified return mode.

        Args:
            dictionary (dict): The dictionary to search through.
            comparator (Callable[[Any], bool]): A function that takes a key or value and returns True if it matches the search criteria.
            nested (bool): Whether to search through nested dictionaries (default is False).
            return_mode (str): Determines the format of the returned results. Options are 'VALUE', 'VALUE_PATH', 'PATH', 'LIST', and 'GENERATOR'. Default is 'PATH'.
            separator (str): The string used to separate keys in the path (default is '//').
            safety (Tuple[bool, bool]): A tuple where the first element enables hyper-safe mode (ensuring all keys are found) and the second element enables hyper-consistent mode (ensuring consistent results across iterations). Default is (False, False).
            path_prefix (str): A prefix to be added to the path of found items (used for nested searches, default is '').
            identifier (str): An optional identifier for error messages in hyper-safe mode (default is '').
            target (str): Determines whether the comparator is applied to keys ('KEY') or values ('VALUE'). Default is 'VALUE'.

        Returns:
            list: A list of results formatted according to the specified return mode, or an async generator if return_mode is 'GENERATOR'.
        """
        gen = LookupDict._generic_finder_generator(
            dictionary=dictionary,
            comparator=comparator,
            nested=nested,
            separator=separator,
            safety=safety,
            path_prefix=path_prefix,
            identifier=identifier,
            target=target,
        )

        if return_mode == "GENERATOR":
            return gen

        finds = []
        imutable_finds = ()

        async for key, value, path, priority in gen:
            if return_mode == "PATH":
                finds.append((key, path, priority))
            elif return_mode == "LIST":
                finds.append(path)
            elif return_mode == "VALUE":
                finds.append(value)
            elif return_mode == "VALUE_PATH":
                finds.append((value, path, priority))
            if safety[1]:
                if not LookupDictHelper._consistency_check(imutable_finds, finds):
                    raise ValueError(
                        "Inconsistent results found during hyper-safe lookup."
                    )
                imutable_finds = tuple(finds)

        return imutable_finds if safety[1] else finds

    @staticmethod
    async def _generic_compare(
        dictionary: dict,
        threshold: Any,
        return_mode: str = "PATH",
        nested: bool = False,
        separator: str = "//",
        safety: Tuple[bool, bool] = (False, False),
        target: str = "VALUE",
    ):
        pass

    # external Methods
    async def find_key_by_value(
        self,
        dictionary: dict,
        threshold: Any,
        comparison: str = "eq",
        return_mode: str = "PATH",
        nested: bool = False,
        separator: str = "//",
        safety: Tuple[bool, bool] = (False, False),
    ) -> Union[list, Tuple, AsyncGenerator[Tuple[Any, Any, str, int], None]]:
        comparator = {
            "eq": lambda x: x == threshold,
            "ne": lambda x: x != threshold,
            "gt": lambda x: x > threshold,
            "lt": lambda x: x < threshold,
            "ge": lambda x: x >= threshold,
            "le": lambda x: x <= threshold,
        }
        return await self._generic_finder(
            dictionary,
            comparator[comparison],
            nested=nested,
            return_mode=return_mode,
            separator=separator,
            safety=safety,
            target="VALUE",
        )

    async def find_value_by_key(
        self,
        dictionary: dict,
        threshold: Any,
        comparison: str = "eq",
        return_mode: str = "PATH",
        nested: bool = False,
        separator: str = "//",
        safety: Tuple[bool, bool] = (False, False),
    ) -> Union[list, Tuple, AsyncGenerator[Tuple[Any, Any, str, int], None]]:
        comparator = {
            "eq": lambda x: x == threshold,
            "ne": lambda x: x != threshold,
            "gt": lambda x: x > threshold,
            "lt": lambda x: x < threshold,
            "ge": lambda x: x >= threshold,
            "le": lambda x: x <= threshold,
        }
        return await self._generic_finder(
            dictionary,
            comparator[comparison],
            nested=nested,
            return_mode=return_mode,
            separator=separator,
            safety=safety,
            target="KEY",
        )
