# external Modules
import pytest
from pathlib import Path
import time, random, os, threading
from multiprocessing import shared_memory

# internal Modules
from tbot223_core import Utils, DecoratorUtils, GlobalVars

@pytest.fixture(scope="module")
def setup_module():
    """
    Fixture to create Utils, DecoratorUtils, and GlobalVars instances for testing.
    """
    base_dir = Path(__file__).resolve().parent
    utils = Utils(is_logging_enabled=True, base_dir=base_dir)
    decorator_utils = DecoratorUtils()
    global_vars = GlobalVars(is_logging_enabled=True, base_dir=base_dir)
    return utils, decorator_utils, global_vars

@pytest.mark.usefixtures("setup_module")
class TestUtils:
    def test_str_to_path(self, setup_module):
        utils, _, _ = setup_module
        path_str = "some/directory/path" if os.name != 'nt' else "some\\directory\\path"
        path_obj = utils.str_to_path(path_str)
        assert path_obj.success, f"Failed to convert string to path: {path_obj.error}"
        assert isinstance(path_obj.data, type(Path())), "Converted data is not a Path object"
        assert str(path_obj.data) == path_str, "Path string does not match the original string"

    def test_hashing(self, setup_module):
        utils, _, _ = setup_module
        original_text = "Hello, World!"

        for algorithm in ["md5", "sha1", "sha256", "sha512"]:
            hashed = utils.hashing(data=original_text, algorithm=algorithm)
            assert hashed.success, f"Hashing with {algorithm} failed: {hashed.error}"
            assert hashed.data != original_text, f"Hashed text with {algorithm} should not match the original text"

    def test_pbkdf2_hmac(self, setup_module):
        utils, _, _ = setup_module
        password = "securepassword"
        salt_size = 16
        iterations = 100000
        algorithm = "sha256"

        result = utils.pbkdf2_hmac(password=password, algorithm=algorithm, salt_size=salt_size, iterations=iterations)
        assert result.success, f"PBKDF2-HMAC failed: {result.error}"

        verified = utils.verify_pbkdf2_hmac(password=password, salt_hex=result.data['salt_hex'], 
                                            hash_hex=result.data['hash_hex'], algorithm=algorithm, iterations=iterations)
        assert verified.success, f"PBKDF2-HMAC verification failed: {verified.error}"
        assert verified.data is True, "PBKDF2-HMAC verification returned False"

    def test_find_keys_by_value(self, setup_module) -> None:
        utils, _, _ = setup_module
        """
        Test the find_keys_by_value method for both nested and non-nested dictionaries.
        """
        # Non-nested dictionary test
        sample_dict = {'a': 1, 'b': 2, 'c': 1, 'd': 3}
        keys = utils.find_keys_by_value(sample_dict, 1, "eq", False).data
        assert set(keys) == {'a', 'c'}

        # Nested dictionary test with return_mod="path" (default separator="/")
        sample_dict_nested = {'a': 1, 'b': {'b1': 2, 'b2': 1}, 'c': 1, 'd': 3}
        keys_nested = utils.find_keys_by_value(sample_dict_nested, 1, "eq", True, separator="/", return_mod="path").data
        assert set(keys_nested) == {'a', 'b/b2', 'c'}

        # Test return_mod="flat" (nested results come as nested lists)
        keys_flat = utils.find_keys_by_value(sample_dict_nested, 1, "eq", True, return_mod="flat").data
        # flat mode returns nested lists for nested dicts
        assert 'a' in keys_flat
        assert 'c' in keys_flat

        # Test return_mod="forest" (returns dict structure)
        keys_forest = utils.find_keys_by_value(sample_dict_nested, 1, "eq", True, return_mod="forest").data
        assert 'a' in keys_forest
        assert 'c' in keys_forest

        # Test separator="tuple" returns tuple
        keys_tuple = utils.find_keys_by_value(sample_dict, 1, "eq", False, separator="tuple").data
        assert isinstance(keys_tuple, tuple)
        assert set(keys_tuple) == {'a', 'c'}

        # Test separator="list" returns list
        keys_list = utils.find_keys_by_value(sample_dict, 1, "eq", False, separator="list").data
        assert isinstance(keys_list, list)
        assert set(keys_list) == {'a', 'c'}

        # Test different comparison operators
        gt_keys = utils.find_keys_by_value(sample_dict, 2, "gt", False).data
        assert set(gt_keys) == {'d'}  # only 'd': 3 is greater than 2

        le_keys = utils.find_keys_by_value(sample_dict, 2, "le", False).data
        assert set(le_keys) == {'a', 'b', 'c'}  # 1, 2, 1 are <= 2

    def test_find_keys_by_value_failure(self, setup_module) -> None:
        utils, _, _ = setup_module
        """
        Test failure scenarios for the find_keys_by_value method.
        """
        # Non-dictionary input test
        non_dict_result = utils.find_keys_by_value("not_a_dict", 1, "eq", False)
        assert non_dict_result.success is False
        assert "Input data must be a dictionary" in non_dict_result.error

        wrong_comparison_result = utils.find_keys_by_value({'a': 1}, 1, "unsupported_op", False)
        assert wrong_comparison_result.success is False
        assert "Unsupported comparison operator: unsupported_op" in wrong_comparison_result.error

        wrong_threshold_result = utils.find_keys_by_value({'a': 1}, ['not', 'a', 'valid', 'type'], "eq", False)
        assert wrong_threshold_result.success is False
        assert "Threshold must be of type str, bool, int, or float" in wrong_threshold_result.error

        # Test invalid nested parameter
        wrong_nested_result = utils.find_keys_by_value({'a': 1}, 1, "eq", "not_a_bool")
        assert wrong_nested_result.success is False
        assert "nested must be a boolean value" in wrong_nested_result.error

        # Test invalid separator parameter
        wrong_separator_result = utils.find_keys_by_value({'a': 1}, 1, "eq", False, separator=123)
        assert wrong_separator_result.success is False
        assert "separator must be a string" in wrong_separator_result.error

        # Test invalid return_mod parameter
        wrong_return_mod_result = utils.find_keys_by_value({'a': 1}, 1, "eq", False, return_mod="invalid")
        assert wrong_return_mod_result.success is False
        assert "return_mod must be one of 'flat', 'forest', or 'path'" in wrong_return_mod_result.error

        # Test separator="list" or "tuple" with return_mod="path" conflict
        conflict_result = utils.find_keys_by_value({'a': 1}, 1, "eq", False, separator="tuple", return_mod="path")
        assert conflict_result.success is False
        assert "separator cannot be 'list' or 'tuple' when return_mod is 'path'" in conflict_result.error

    @pytest.mark.performance
    def test_find_keys_by_value_performance(self, setup_module) -> None:
        """
        Performance test for the find_keys_by_value method with a large nested dictionary.
        
        WARNING: This test operates on 10,000+ keys with nested structures.
        May timeout or fail on systems with limited memory or CPU resources.
        """
        utils, _, _ = setup_module
        large_dict = {f'key_{i}': random.randint(1, 100) for i in range(10000)}
        nested_large_dict = {f'key_{i}': {'subkey_{j}': random.randint(1, 100) for j in range(10)} for i in range(1000)}
        large_dict.update(nested_large_dict)
        result = utils.find_keys_by_value(large_dict, 50, "eq", True)
        assert result.success is True

@pytest.mark.usefixtures("setup_module")
class TestDecoratorUtils:
    def test_count_runtime(self, setup_module):
        _, decorator_utils, _ = setup_module

        @decorator_utils.count_runtime()
        def sample_function(delay_time):
            time.sleep(delay_time)
            return "Completed"

        delay = 1  # seconds
        result = sample_function(delay)
        assert result == "Completed", "Sample function did not return expected result"

@pytest.mark.usefixtures("setup_module")
class TestGlobalVars:
    def test_set_and_get_global_var(self, setup_module):
        _, _, global_vars = setup_module

        key = "test_var"
        value = 42

        # Set global variable
        set_result = global_vars.set(key, value)
        assert set_result.success, f"Failed to set global variable: {set_result.error}"

        # Get global variable
        get_result = global_vars.get(key)
        assert get_result.success, f"Failed to get global variable: {get_result.error}"
        assert get_result.data == value, "Retrieved value does not match the set value"

        # Test overwriting the variable
        new_value = 100
        set_result = global_vars.set(key, new_value, overwrite=True)
        assert set_result.success, f"Failed to overwrite global variable: {set_result.error}"
        get_result = global_vars.get(key)
        assert get_result.success, f"Failed to get overwritten global variable: {get_result.error}"
        assert get_result.data == new_value, "Retrieved value does not match the overwritten value"

    def test_attribute_access(self, setup_module):
        _, _, global_vars = setup_module

        key = "attr_var"
        value = "attribute_value"

        # Set global variable
        global_vars.attr_var = value

        # Access as attribute
        attr_value = global_vars.attr_var
        assert attr_value == value, "Attribute access did not return the expected value"

    def test_call_syntax(self, setup_module):
        _, _, global_vars = setup_module

        key = "call_var"
        value = [1, 2, 3]

        # Set global variable
        set_result = global_vars(key, value)
        assert set_result.success, f"Failed to set global variable: {set_result.error}"

        # Access using call syntax
        call_value = global_vars(key)
        assert call_value.data == value, "Call syntax did not return the expected value"

    def test_call_syntax_allows_none_value(self, setup_module):
        _, _, global_vars = setup_module

        key = "none_var"

        set_result = global_vars(key, None)
        assert set_result.success, f"Failed to set None value: {set_result.error}"

        get_result = global_vars(key)
        assert get_result.success, f"Failed to get None value: {get_result.error}"
        assert get_result.data is None, "Call syntax should store None as a real value"

    def test_missing_attribute_raises_attribute_error(self, setup_module):
        _, _, global_vars = setup_module

        assert hasattr(global_vars, "missing_attr") is False
        with pytest.raises(AttributeError):
            _ = global_vars.missing_attr
    
    def test_delete_global_var(self, setup_module):
        _, _, global_vars = setup_module

        key = "delete_var"
        value = "to be deleted"

        # Set global variable
        set_result = global_vars.set(key, value)
        assert set_result.success, f"Failed to set global variable: {set_result.error}"

        # Delete global variable
        delete_result = global_vars.delete(key)
        assert delete_result.success, f"Failed to delete global variable: {delete_result.error}"

        # Try to get deleted variable
        get_result = global_vars.get(key)
        assert not get_result.success, "Deleted variable should not be retrievable"

    def test_clear_global_vars(self, setup_module):
        _, _, global_vars = setup_module

        # Set multiple global variables
        global_vars.set("var1", 1)
        global_vars.set("var2", 2)

        # Clear all global variables
        clear_result = global_vars.clear()
        assert clear_result.success, f"Failed to clear global variables: {clear_result.error}"

        # Verify that variables are cleared
        get_result1 = global_vars.get("var1")
        get_result2 = global_vars.get("var2")
        assert not get_result1.success, "var1 should not be retrievable after clear"
        assert not get_result2.success, "var2 should not be retrievable after clear"

    def test_list_global_vars(self, setup_module):
        _, _, global_vars = setup_module

        # Clear any existing variables
        global_vars.clear()

        # Set multiple global variables
        global_vars.set("list_var1", "value1")
        global_vars.set("list_var2", "value2")

        # List global variables
        list_result = global_vars.list_vars()
        assert list_result.success, f"Failed to list global variables: {list_result.error}"
        assert "list_var1" in list_result.data, "list_var1 not found in global variables list"
        assert "list_var2" in list_result.data, "list_var2 not found in global variables list"
        
    def test_exists_global_var(self, setup_module):
        _, _, global_vars = setup_module

        key = "exists_var"
        value = "exists"

        # Ensure variable does not exist
        exists_result = global_vars.exists(key)
        assert exists_result.success, f"Exists check failed: {exists_result.error}"
        assert exists_result.data is False, "Variable should not exist yet"

        # Set global variable
        global_vars.set(key, value)

        # Check existence again
        exists_result = global_vars.exists(key)
        assert exists_result.success, f"Exists check failed: {exists_result.error}"
        assert exists_result.data is True, "Variable should exist now"
        
    def test_nonexistent_var_access(self, setup_module):
        _, _, global_vars = setup_module

        key = "nonexistent_var"

        # Try to get a nonexistent variable
        get_result = global_vars.get(key)
        assert not get_result.success, "Getting a nonexistent variable should fail"

        # Try to delete a nonexistent variable
        delete_result = global_vars.delete(key)
        assert not delete_result.success, "Deleting a nonexistent variable should fail"

    def test_overwrite_protection(self, setup_module):
        _, _, global_vars = setup_module

        key = "protected_var"
        value = "initial_value"

        # Set global variable
        global_vars.set(key, value)

        # Attempt to overwrite without permission
        set_result = global_vars.set(key, "new_value", overwrite=False)
        assert not set_result.success, "Overwriting without permission should fail"

        # Verify value remains unchanged
        get_result = global_vars.get(key)
        assert get_result.success, f"Failed to get variable: {get_result.error}"
        assert get_result.data == value, "Variable value should remain unchanged"

class TestEdgeCases:
    def test_empty_key(self, setup_module):
        _, _, global_vars = setup_module

        key = ""
        value = "empty_key_value"

        # Set global variable with empty key
        set_result = global_vars.set(key, value)
        assert not set_result.success, "Setting a variable with an empty key should fail"

        # Get global variable with empty key
        get_result = global_vars.get(key)
        assert not get_result.success, "Getting a variable with an empty key should fail"

        # set None as key
        key = None
        set_result = global_vars.set(key, value)
        assert not set_result.success, "Setting a variable with None as key should fail"
        assert "ValueError" in set_result.error, "None key should fail with ValueError"
        get_result = global_vars.get(key)
        assert not get_result.success, "Getting a variable with None as key should fail"

        key = 123
        set_result = global_vars.set(key, value)
        assert not set_result.success, "Setting a variable with non-string key should fail"
        assert "ValueError" in set_result.error, "Non-string key should fail with ValueError"

    @pytest.mark.performance
    def test_global_var_extreme_change(self, setup_module):
        """
        Extreme scale test: setting and managing 50,000 global variables.
        
        WARNING: This test creates/deletes 50,000+ variables.
        May timeout or fail on systems with limited memory or under heavy load.
        """
        _, _, global_vars = setup_module

        # Extreme change test: setting a very large number of global variables
        num_vars = 50000
        for i in range(num_vars):
            key = f"var_{i}"
            value = i
            set_result = global_vars.set(key, value)
            assert set_result.success, f"Failed to set global variable {key}: {set_result.error}"

        # Verify a few random variables
        for i in random.sample(range(num_vars), 10):
            key = f"var_{i}"
            get_result = global_vars.get(key)
            assert get_result.success, f"Failed to get global variable {key}: {get_result.error}"
            assert get_result.data == i, f"Value mismatch for {key}: expected {i}, got {get_result.data}"

        # del and re-write some variables
        for i in random.sample(range(num_vars), 5000):
            key = f"var_{i}"
            delete_result = global_vars.delete(key)
            assert delete_result.success, f"Failed to delete global variable {key}: {delete_result.error}"
            set_result = global_vars.set(key, i * 2)
            assert set_result.success, f"Failed to reset global variable {key}: {set_result.error}"
            get_result = global_vars.get(key)
            assert get_result.success, f"Failed to get reset global variable {key}: {get_result.error}"
            assert get_result.data == i * 2, f"Value mismatch for reset {key}: expected {i * 2}, got {get_result.data}"

        # Clean up
        clear_result = global_vars.clear()
        assert clear_result.success, f"Failed to clear global variables after extreme change test: {clear_result.error}"
        
    def test_global_vars_concurrency(self, setup_module):
        _, _, global_vars = setup_module

        key = "concurrent_var"
        global_vars.set(key, 0)

        iterations = 1000
        lock = threading.RLock()

        def increment_var():
            with lock:
                current_value = global_vars.get(key).data
                global_vars.set(key, current_value + 1, overwrite=True)

        threads = []
        for _ in range(iterations):
            thread = threading.Thread(target=increment_var)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        result = global_vars.get(key)
        assert result.success, f"Failed to get concurrent variable: {result.error}"
        assert result.data == iterations, f"Concurrent increment failed: expected {iterations}, got {result.data}"

    # I WILL ADD MORE EDGE CASE TESTS HERE IN THE FUTURE


@pytest.mark.usefixtures("setup_module")
class TestSharedMemory:
    """Tests for GlobalVars Shared Memory (SHM) functionality"""
    
    def test_shm_gen_basic(self, setup_module):
        """Test basic shared memory generation"""
        _, _, global_vars = setup_module
        
        shm_name = "test_shm_basic"
        size = 1024
        
        # Generate shared memory
        result = global_vars.shm_gen(name=shm_name, size=size, create_lock=False)
        assert result.success, f"Failed to generate shared memory: {result.error}"
        
        # Clean up
        close_result = global_vars.shm_close(shm_name)
        assert close_result.success, f"Failed to close shared memory: {close_result.error}"
    
    def test_shm_gen_with_lock(self, setup_module):
        """Test shared memory generation with lock"""
        _, _, global_vars = setup_module
        
        shm_name = "test_shm_lock"
        size = 1024
        
        # Generate shared memory with lock
        result = global_vars.shm_gen(name=shm_name, size=size, create_lock=True)
        assert result.success, f"Failed to generate shared memory with lock: {result.error}"
        assert result.data is not None, "Lock should be returned"
        
        # Clean up
        global_vars.shm_close(shm_name)
    
    def test_shm_sync_and_update_pickle(self, setup_module):
        """Test shared memory sync and update with pickle serialization"""
        _, _, global_vars = setup_module
        
        shm_name = "test_shm_sync_pickle"
        size = 4096
        
        # Clear any existing variables
        global_vars.clear()
        
        # Generate shared memory
        gen_result = global_vars.shm_gen(name=shm_name, size=size, create_lock=False)
        assert gen_result.success, f"Failed to generate shared memory: {gen_result.error}"
        
        # Set some variables
        global_vars.set("sync_var1", 42)
        global_vars.set("sync_var2", "hello")
        global_vars.set("sync_var3", [1, 2, 3])
        
        # Sync to shared memory
        sync_result = global_vars.shm_sync(shm_name, serialize_format="pickle")
        assert sync_result.success, f"Failed to sync to shared memory: {sync_result.error}"
        
        # Clear variables
        global_vars.clear()
        
        # Verify variables are cleared
        assert not global_vars.get("sync_var1").success, "Variable should be cleared"
        
        # Update from shared memory
        update_result = global_vars.shm_update(shm_name, serialize_format="pickle")
        assert update_result.success, f"Failed to update from shared memory: {update_result.error}"
        
        # Verify variables are restored
        assert global_vars.get("sync_var1").data == 42, "sync_var1 should be restored"
        assert global_vars.get("sync_var2").data == "hello", "sync_var2 should be restored"
        assert global_vars.get("sync_var3").data == [1, 2, 3], "sync_var3 should be restored"
        
        # Clean up
        global_vars.shm_close(shm_name)
        global_vars.clear()
    
    def test_shm_sync_and_update_json(self, setup_module):
        """Test shared memory sync and update with JSON serialization"""
        _, _, global_vars = setup_module
        
        shm_name = "test_shm_sync_json"
        size = 4096
        
        # Clear any existing variables
        global_vars.clear()
        
        # Generate shared memory
        gen_result = global_vars.shm_gen(name=shm_name, size=size, create_lock=False)
        assert gen_result.success, f"Failed to generate shared memory: {gen_result.error}"
        
        # Set some JSON-serializable variables
        global_vars.set("json_var1", 100)
        global_vars.set("json_var2", "world")
        global_vars.set("json_var3", {"key": "value"})
        
        # Sync to shared memory with JSON
        sync_result = global_vars.shm_sync(shm_name, serialize_format="json")
        assert sync_result.success, f"Failed to sync to shared memory with JSON: {sync_result.error}"
        
        # Clear variables
        global_vars.clear()
        
        # Update from shared memory with JSON
        update_result = global_vars.shm_update(shm_name, serialize_format="json")
        assert update_result.success, f"Failed to update from shared memory with JSON: {update_result.error}"
        
        # Verify variables are restored
        assert global_vars.get("json_var1").data == 100, "json_var1 should be restored"
        assert global_vars.get("json_var2").data == "world", "json_var2 should be restored"
        assert global_vars.get("json_var3").data == {"key": "value"}, "json_var3 should be restored"
        
        # Clean up
        global_vars.shm_close(shm_name)
        global_vars.clear()
    
    def test_shm_get(self, setup_module):
        """Test getting shared memory object"""
        _, _, global_vars = setup_module
        
        shm_name = "test_shm_get"
        size = 1024
        
        # Generate shared memory
        global_vars.shm_gen(name=shm_name, size=size, create_lock=False)
        
        # Get shared memory
        get_result = global_vars.shm_get(shm_name)
        assert get_result.success, f"Failed to get shared memory: {get_result.error}"
        assert get_result.data is not None, "Shared memory object should be returned"
        assert get_result.data.name == shm_name, "Shared memory name should match"
        
        # Clean up
        global_vars.shm_close(shm_name)
    
    def test_shm_connect(self, setup_module):
        """Test connecting to existing shared memory"""
        _, _, global_vars = setup_module
        
        shm_name = "test_shm_connect"
        size = 1024
        
        # Generate shared memory
        global_vars.shm_gen(name=shm_name, size=size, create_lock=False)
        
        # Create a new GlobalVars instance to simulate another process
        new_global_vars = GlobalVars(is_logging_enabled=False)
        
        # Connect to existing shared memory
        connect_result = new_global_vars.shm_connect(shm_name)
        assert connect_result.success, f"Failed to connect to shared memory: {connect_result.error}"
        
        # Clean up
        new_global_vars.shm_close(shm_name, close_only=True)
        global_vars.shm_close(shm_name)
    
    def test_shm_close_only(self, setup_module):
        """Test closing shared memory without unlinking"""
        _, _, global_vars = setup_module
        
        shm_name = "test_shm_close_only"
        size = 1024
        
        # Generate shared memory
        global_vars.shm_gen(name=shm_name, size=size, create_lock=False)
        
        # Close only (don't unlink) - Note: behavior may differ between Windows and Unix
        close_result = global_vars.shm_close(shm_name, close_only=True)
        assert close_result.success, f"Failed to close shared memory: {close_result.error}"
        
        # On Windows, shared memory may be freed immediately after close
        # Try to reconnect - may or may not succeed depending on OS
        connect_result = global_vars.shm_connect(shm_name)
        if connect_result.success:
            # If reconnect succeeded, do full close
            global_vars.shm_close(shm_name)
        # Test passes regardless - we just verify close_only doesn't error
    
    def test_shm_cache_management(self, setup_module):
        """Test shared memory cache management"""
        _, _, global_vars = setup_module
        
        # Create multiple shared memory objects to test cache limits
        shm_names = [f"test_cache_{i}" for i in range(3)]
        
        for name in shm_names:
            result = global_vars.shm_gen(name=name, size=512, create_lock=False)
            assert result.success, f"Failed to generate shared memory {name}: {result.error}"
        
        # Clear cache
        cache_result = global_vars.shm_cache_management(None, None)
        assert cache_result.success, f"Failed to clear shared memory cache: {cache_result.error}"
        
        # Clean up
        for name in shm_names:
            try:
                global_vars.shm_close(name)
            except:
                pass

    def test_shm_cache_eviction_warns_for_owned_memory(self, monkeypatch):
        """Test cache eviction warns when the current process owns the shared memory."""
        global_vars = GlobalVars(is_logging_enabled=False, shared_memory_cache_max_size=1)
        messages = []
        monkeypatch.setattr(
            GlobalVars,
            "_log",
            lambda self, level, message: messages.append((level, message)),
        )

        shm_name_1 = f"test_cache_owner_warn_1_{os.getpid()}"
        shm_name_2 = f"test_cache_owner_warn_2_{os.getpid()}"

        global_vars.shm_gen(name=shm_name_1, size=512, create_lock=False)
        global_vars.shm_gen(name=shm_name_2, size=512, create_lock=False)

        assert any(level == "WARNING" and "Call shm_close() explicitly to unlink" in message for level, message in messages)

        global_vars.shm_close(shm_name_1)
        global_vars.shm_close(shm_name_2)
    
    def test_shm_lock_method(self, setup_module):
        """Test the lock() method for GlobalVars"""
        _, _, global_vars = setup_module
        
        lock = global_vars.lock()
        assert lock is not None, "Lock should be returned"
        
        # Test using lock
        with lock:
            global_vars.set("lock_test", "value")
            assert global_vars.get("lock_test").data == "value"
        
        global_vars.delete("lock_test")
    
    def test_shm_context_manager(self, setup_module):
        """Test GlobalVars as context manager"""
        _, _, global_vars = setup_module
        
        # Test using context manager (acquires lock)
        with global_vars:
            global_vars.set("context_test", 123)
            assert global_vars.get("context_test").data == 123
        
        global_vars.delete("context_test")


@pytest.mark.usefixtures("setup_module")
class TestSharedMemoryFailures:
    """Tests for GlobalVars Shared Memory failure scenarios"""
    
    def test_shm_gen_invalid_name(self, setup_module):
        """Test shared memory generation with invalid name"""
        _, _, global_vars = setup_module
        
        # Empty name
        result = global_vars.shm_gen(name="", size=1024)
        assert not result.success, "Empty name should fail"
        
        # None name
        result = global_vars.shm_gen(name=None, size=1024)
        assert not result.success, "None name should fail"
    
    def test_shm_gen_invalid_size(self, setup_module):
        """Test shared memory generation with invalid size"""
        _, _, global_vars = setup_module
        
        # Zero size
        result = global_vars.shm_gen(name="test_invalid_size", size=0)
        assert not result.success, "Zero size should fail"
        
        # Negative size
        result = global_vars.shm_gen(name="test_invalid_size", size=-100)
        assert not result.success, "Negative size should fail"

    def test_shm_gen_existing_smaller_shared_memory_fails(self, setup_module):
        """Test shm_gen fails when an existing shared memory block is smaller than requested."""
        _, _, global_vars = setup_module

        shm_name = f"test_size_mismatch_{os.getpid()}"
        existing = shared_memory.SharedMemory(create=True, size=128, name=shm_name)
        try:
            result = global_vars.shm_gen(name=shm_name, size=100000, create_lock=False)
            assert not result.success, "Connecting to too-small existing shared memory should fail"
            assert "Existing SHM" in str(result.data) or "requested" in str(result.data)
        finally:
            existing.close()
            existing.unlink()
    
    def test_shm_sync_nonexistent(self, setup_module):
        """Test syncing to nonexistent shared memory"""
        _, _, global_vars = setup_module
        
        result = global_vars.shm_sync("nonexistent_shm")
        assert not result.success, "Syncing to nonexistent shared memory should fail"
    
    def test_shm_sync_invalid_format(self, setup_module):
        """Test syncing with invalid serialization format"""
        _, _, global_vars = setup_module
        
        shm_name = "test_invalid_format"
        global_vars.shm_gen(name=shm_name, size=1024, create_lock=False)
        
        result = global_vars.shm_sync(shm_name, serialize_format="invalid_format")
        assert not result.success, "Invalid serialization format should fail"
        
        global_vars.shm_close(shm_name)
    
    def test_shm_close_nonexistent(self, setup_module):
        """Test closing nonexistent shared memory"""
        _, _, global_vars = setup_module
        
        result = global_vars.shm_close("nonexistent_shm")
        assert not result.success, "Closing nonexistent shared memory should fail"
    
    def test_shm_memory_overflow(self, setup_module):
        """Test syncing data larger than shared memory size"""
        _, _, global_vars = setup_module
        
        shm_name = f"test_ovfl_{os.getpid()}"
        small_size = 64  # Request small size (OS may page-align to 4096+)
        
        # Ensure no stale shared memory exists
        try:
            stale = shared_memory.SharedMemory(name=shm_name)
            stale.close()
            stale.unlink()
        except FileNotFoundError:
            pass
        
        global_vars.shm_gen(name=shm_name, size=small_size, create_lock=False)
        
        # Set a variable large enough to exceed even page-aligned shared memory (typically 4096)
        global_vars.set("large_var", "x" * 100000)
        
        # Try to sync - should fail due to size
        result = global_vars.shm_sync(shm_name)
        assert not result.success, "Syncing data larger than shared memory should fail"
        
        global_vars.delete("large_var")
        global_vars.shm_close(shm_name)


@pytest.mark.usefixtures("setup_module")
class TestUtilsMethods:
    """Tests for Utils class methods that were missing"""
    
    def test_insert_at_intervals_list(self, setup_module):
        """Test insert_at_intervals with list"""
        utils, _, _ = setup_module
        
        data_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        result = utils.insert_at_intervals(data_list, 3, 'X', at_start=True)
        assert result.success, f"insert_at_intervals failed: {result.error}"
        assert result.data[0] == 'X', "X should be inserted at start"
    
    def test_insert_at_intervals_string(self, setup_module):
        """Test insert_at_intervals with string"""
        utils, _, _ = setup_module
        
        data_str = "abcdefghi"
        result = utils.insert_at_intervals(data_str, 3, '-', at_start=False)
        assert result.success, f"insert_at_intervals failed: {result.error}"
        assert isinstance(result.data, str), "Result should be a string"
    
    def test_insert_at_intervals_at_start_false(self, setup_module):
        """Test insert_at_intervals with at_start=False"""
        utils, _, _ = setup_module
        
        data_list = [1, 2, 3, 4, 5, 6]
        result = utils.insert_at_intervals(data_list, 2, 'X', at_start=False)
        assert result.success, f"insert_at_intervals failed: {result.error}"
        assert result.data[0] != 'X', "X should not be at start when at_start=False"
    
    def test_insert_at_intervals_invalid_data(self, setup_module):
        """Test insert_at_intervals with invalid data type"""
        utils, _, _ = setup_module
        
        result = utils.insert_at_intervals(12345, 2, 'X')
        assert not result.success, "Invalid data type should fail"
    
    def test_insert_at_intervals_invalid_interval(self, setup_module):
        """Test insert_at_intervals with invalid interval"""
        utils, _, _ = setup_module
        
        result = utils.insert_at_intervals([1, 2, 3], 0, 'X')
        assert not result.success, "Zero interval should fail"
        
        result = utils.insert_at_intervals([1, 2, 3], -1, 'X')
        assert not result.success, "Negative interval should fail"

    def test_insert_at_intervals_invalid_at_start(self, setup_module):
        """Test insert_at_intervals with non-boolean at_start"""
        utils, _, _ = setup_module
        
        result = utils.insert_at_intervals([1, 2, 3], 2, 'X', at_start="yes")
        assert not result.success, "Non-boolean at_start should fail"


@pytest.mark.usefixtures("setup_module")
class TestHashingFailures:
    """Tests for hashing method failure cases"""
    
    def test_hashing_invalid_algorithm(self, setup_module):
        """Test hashing with invalid algorithm"""
        utils, _, _ = setup_module
        
        result = utils.hashing("test_data", algorithm="invalid_algo")
        assert not result.success, "Invalid algorithm should fail"
        assert "Unsupported algorithm" in str(result.data) or "unsupported" in result.error.lower()
    
    def test_hashing_non_string_data(self, setup_module):
        """Test hashing with non-string data"""
        utils, _, _ = setup_module
        
        result = utils.hashing(12345, algorithm="sha256")
        assert not result.success, "Non-string data should fail"
        assert "must be a string" in str(result.data) or "string" in result.error.lower()
    
    def test_hashing_none_data(self, setup_module):
        """Test hashing with None data"""
        utils, _, _ = setup_module
        
        result = utils.hashing(None, algorithm="sha256")
        assert not result.success, "None data should fail"
    
    def test_hashing_empty_string(self, setup_module):
        """Test hashing with empty string"""
        utils, _, _ = setup_module
        
        result = utils.hashing("", algorithm="sha256")
        assert result.success, "Empty string should be hashable"
        assert len(result.data) > 0, "Hash should not be empty"


@pytest.mark.usefixtures("setup_module")
class TestPBKDF2Failures:
    """Tests for PBKDF2 HMAC failure cases"""
    
    def test_pbkdf2_invalid_algorithm(self, setup_module):
        """Test pbkdf2_hmac with invalid algorithm"""
        utils, _, _ = setup_module
        
        result = utils.pbkdf2_hmac(
            password="test_password",
            algorithm="md5",  # md5 is not supported for pbkdf2
            iterations=100000,
            salt_size=16
        )
        assert not result.success, "Invalid algorithm should fail"
    
    def test_pbkdf2_non_string_password(self, setup_module):
        """Test pbkdf2_hmac with non-string password"""
        utils, _, _ = setup_module
        
        result = utils.pbkdf2_hmac(
            password=12345,  # Not a string
            algorithm="sha256",
            iterations=100000,
            salt_size=16
        )
        assert not result.success, "Non-string password should fail"
    
    def test_pbkdf2_zero_iterations(self, setup_module):
        """Test pbkdf2_hmac with zero iterations"""
        utils, _, _ = setup_module
        
        result = utils.pbkdf2_hmac(
            password="test_password",
            algorithm="sha256",
            iterations=0,
            salt_size=16
        )
        assert not result.success, "Zero iterations should fail"
    
    def test_pbkdf2_negative_iterations(self, setup_module):
        """Test pbkdf2_hmac with negative iterations"""
        utils, _, _ = setup_module
        
        result = utils.pbkdf2_hmac(
            password="test_password",
            algorithm="sha256",
            iterations=-100,
            salt_size=16
        )
        assert not result.success, "Negative iterations should fail"
    
    def test_pbkdf2_zero_salt_size(self, setup_module):
        """Test pbkdf2_hmac with zero salt size"""
        utils, _, _ = setup_module
        
        result = utils.pbkdf2_hmac(
            password="test_password",
            algorithm="sha256",
            iterations=100000,
            salt_size=0
        )
        assert not result.success, "Zero salt size should fail"
    
    def test_verify_pbkdf2_wrong_password(self, setup_module):
        """Test verify_pbkdf2_hmac with wrong password"""
        utils, _, _ = setup_module
        
        # Generate hash
        gen_result = utils.pbkdf2_hmac(
            password="correct_password",
            algorithm="sha256",
            iterations=100000,
            salt_size=16
        )
        assert gen_result.success, "Hash generation should succeed"
        
        # Verify with wrong password
        verify_result = utils.verify_pbkdf2_hmac(
            password="wrong_password",
            salt_hex=gen_result.data["salt_hex"],
            hash_hex=gen_result.data["hash_hex"],
            iterations=gen_result.data["iterations"],
            algorithm=gen_result.data["algorithm"]
        )
        assert verify_result.success, "Verification should succeed (just return False)"
        assert verify_result.data is False, "Wrong password should return False"
    
    def test_verify_pbkdf2_invalid_salt_hex(self, setup_module):
        """Test verify_pbkdf2_hmac with invalid salt hex"""
        utils, _, _ = setup_module
        
        result = utils.verify_pbkdf2_hmac(
            password="test_password",
            salt_hex="not_valid_hex",
            hash_hex="abc123",
            iterations=100000,
            algorithm="sha256"
        )
        assert not result.success, "Invalid salt hex should fail"

    def test_verify_pbkdf2_non_string_salt_hex(self, setup_module):
        """Test verify_pbkdf2_hmac with non-string salt_hex"""
        utils, _, _ = setup_module
        
        result = utils.verify_pbkdf2_hmac(
            password="test_password",
            salt_hex=12345,
            hash_hex="abc123",
            iterations=100000,
            algorithm="sha256"
        )
        assert not result.success, "Non-string salt_hex should fail"

    def test_verify_pbkdf2_non_string_hash_hex(self, setup_module):
        """Test verify_pbkdf2_hmac with non-string hash_hex"""
        utils, _, _ = setup_module
        
        result = utils.verify_pbkdf2_hmac(
            password="test_password",
            salt_hex="abc123",
            hash_hex=12345,
            iterations=100000,
            algorithm="sha256"
        )
        assert not result.success, "Non-string hash_hex should fail"


@pytest.mark.usefixtures("setup_module")
class TestStrToPath:
    """Tests for str_to_path method"""
    
    def test_str_to_path_already_path(self, setup_module):
        """Test str_to_path with Path object input"""
        utils, _, _ = setup_module
        
        path_obj = Path("/some/path")
        result = utils.str_to_path(path_obj)
        assert result.success, "Path object input should succeed"
        # When input is not a string, it returns the input as-is
        assert result.data == path_obj
    
    def test_str_to_path_integer_input(self, setup_module):
        """Test str_to_path with integer input"""
        utils, _, _ = setup_module
        
        result = utils.str_to_path(12345)
        assert result.success, "Non-string input returns input as-is"
        assert result.data == 12345
    
    def test_str_to_path_empty_string(self, setup_module):
        """Test str_to_path with empty string"""
        utils, _, _ = setup_module
        
        result = utils.str_to_path("")
        assert result.success, "Empty string should be convertible"
        assert isinstance(result.data, Path)
    
    def test_str_to_path_special_characters(self, setup_module):
        """Test str_to_path with special characters"""
        utils, _, _ = setup_module
        
        special_path = "path/with spaces/and-dashes/and_underscores"
        result = utils.str_to_path(special_path)
        assert result.success, "Path with special characters should succeed"
        assert isinstance(result.data, Path)


@pytest.mark.usefixtures("setup_module")
class TestDecoratorUtilsMethods:
    """Additional tests for DecoratorUtils"""
    
    def test_count_runtime_with_exception(self, setup_module):
        """Test count_runtime with function that raises exception"""
        _, decorator_utils, _ = setup_module
        
        @decorator_utils.count_runtime()
        def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_func()

    def test_count_runtime_preserves_function_metadata(self, setup_module):
        """Test that count_runtime preserves function name and docstring via functools.wraps"""
        _, decorator_utils, _ = setup_module

        @decorator_utils.count_runtime()
        def my_named_function():
            """My docstring."""
            return 42

        assert my_named_function.__name__ == "my_named_function"
        assert my_named_function.__doc__ == "My docstring."


if __name__ == "__main__":
    pytest.main([__file__, "-m not performance"])
