# external Modules
import pytest
from pathlib import Path
from unittest.mock import patch

# internal Modules
from tbot223_core import FileManager

@pytest.fixture(scope="module")
def file_manager():
    """
    Fixture to create a FileManager instance for testing.
    """
    base_dir = Path(__file__).resolve().parent
    file_manager = FileManager(base_dir=base_dir)
    return file_manager

@pytest.mark.usefixtures("tmp_path", "file_manager")
class TestFileManager:
    def test_atomic_write_and_read(self, file_manager, tmp_path):
        test_file = tmp_path / "test_atomic.txt"
        test_data = "This is a test string for atomic write and read."

        # Test atomic write
        write_result = file_manager.atomic_write(file_path=test_file, data=test_data)
        assert write_result.success, f"Atomic write failed: {write_result.error}"

        # Test atomic read
        read_result = file_manager.read_file(file_path=test_file, as_bytes=False)
        assert read_result.success, f"Atomic read failed: {read_result.error}"
        assert read_result.data == test_data, "Data read does not match data written."

        # Test atomic write in bytes mode
        test_data_bytes = b"This is a test byte string for atomic write and read."
        write_result_bytes = file_manager.atomic_write(file_path=test_file, data=test_data_bytes)
        assert write_result_bytes.success, f"Atomic write (bytes) failed: {write_result_bytes.error}"

        # Test atomic read in bytes mode
        read_result_bytes = file_manager.read_file(file_path=test_file, as_bytes=True)
        assert read_result_bytes.success, f"Atomic read (bytes) failed: {read_result_bytes.error}"
        assert read_result_bytes.data == test_data_bytes, "Byte data read does not match byte data written."

    def test_write_json_and_read_json(self, file_manager, tmp_path):
        test_file = tmp_path / "test_data.json"
        test_data = {"key1": "value1", "key2": 2, "key3": [1, 2, 3]}

        # Test write JSON
        write_result = file_manager.write_json(file_path=test_file, data=test_data)
        assert write_result.success, f"Write JSON failed: {write_result.error}"

        # Test read JSON
        read_result = file_manager.read_json(file_path=test_file)
        assert read_result.success, f"Read JSON failed: {read_result.error}"
        assert read_result.data == test_data, "JSON data read does not match data written."

    def test_list_of_files(self, file_manager, tmp_path):
        # Create test files
        (tmp_path / "file1.txt").write_text("File 1")
        (tmp_path / "file2.log").write_text("File 2")
        (tmp_path / "file3.txt").write_text("File 3")

        # Test listing .txt files
        list_result = file_manager.list_of_files(dir_path=tmp_path, extensions=[".txt"], only_name=True)
        assert list_result.success, f"List of files failed: {list_result.error}"
        expected_files = {"file1", "file3"}
        assert set(list_result.data) == expected_files, "Listed files do not match expected files."

        #Test No extension filter and full paths
        list_result_all = file_manager.list_of_files(dir_path=tmp_path, extensions=[], only_name=False)
        assert list_result_all.success, f"List of files failed: {list_result_all.error}"
        expected_files_all = {str(tmp_path / "file1.txt"), str(tmp_path / "file2.log"), str(tmp_path / "file3.txt")}
        assert set(list_result_all.data) == expected_files_all, "Listed files do not match expected files."

    def test_delete_file(self, file_manager, tmp_path):
        test_file = tmp_path / "test_delete.txt"
        test_file.write_text("This file will be deleted.")

        # Ensure file exists
        assert test_file.exists(), "Test file does not exist before deletion."

        # Test delete file
        delete_result = file_manager.delete_file(file_path=test_file)
        assert delete_result.success, f"Delete file failed: {delete_result.error}"

        # Ensure file is deleted
        assert not test_file.exists(), "Test file still exists after deletion."

    def test_delete_directory(self, file_manager, tmp_path):
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("File 1")
        (test_dir / "file2.txt").write_text("File 2")

        # Ensure directory exists
        assert test_dir.exists() and test_dir.is_dir(), "Test directory does not exist before deletion."

        # Test delete directory
        delete_result = file_manager.delete_directory(dir_path=test_dir)
        assert delete_result.success, f"Delete directory failed: {delete_result.error}"

        # Ensure directory is deleted
        assert not test_dir.exists(), "Test directory still exists after deletion."

    def test_create_directory(self, file_manager, tmp_path):
        test_dir = tmp_path / "new_test_dir"

        # Test create directory
        create_result = file_manager.create_directory(dir_path=test_dir)
        assert create_result.success, f"Create directory failed: {create_result.error}"

        # Ensure directory is created
        assert test_dir.exists() and test_dir.is_dir(), "Test directory was not created."

    def test_exist(self, file_manager, tmp_path):
        test_file = tmp_path / "test_exist.txt"
        test_file.write_text("This file is for existence check.")

        # Test exist for existing file
        exist_result = file_manager.exist(path=test_file)
        assert exist_result.success, f"Exist check failed: {exist_result.error}"
        assert exist_result.data is True, "Exist check returned False for existing file."

        # Test exist for non-existing file
        non_exist_file = tmp_path / "non_existing.txt"
        exist_result_non = file_manager.exist(path=non_exist_file)
        assert exist_result_non.success, f"Exist check failed: {exist_result_non.error}"
        assert exist_result_non.data is False, "Exist check returned True for non-existing file."

    def test_with_exit(self, file_manager, tmp_path):
        test_file = tmp_path / "test_with.txt"
        test_data = "This is a test string for with context manager."

        # Use FileManager as a context manager to write to a file
        with file_manager as fm:
            write_result = fm.atomic_write(file_path=test_file, data=test_data)
            assert write_result.success, f"Atomic write in context manager failed: {write_result.error}"

        # Use FileManager as a context manager to read from the file
        with file_manager as fm:
            read_result = fm.read_file(file_path=test_file, as_bytes=False)
            assert read_result.success, f"Atomic read in context manager failed: {read_result.error}"
            assert read_result.data == test_data, "Data read in context manager does not match data written."

@pytest.mark.usefixtures("tmp_path", "file_manager")
class TestFileManagerXfails:
    def test_read_nonexistent_file(self, file_manager, tmp_path):
        nonexistent_file = tmp_path / "nonexistent.txt"

        # Test reading a non-existent file
        read_result = file_manager.read_file(file_path=nonexistent_file, as_bytes=False)
        assert not read_result.success, "Read operation unexpectedly succeeded for a non-existent file."
        assert "FileNotFoundError" in read_result.error, "Error is not FileNotFoundError for non-existent file."

class TestFileManagerEdgeCases:
    def test_atomic_write_failure_protection(self, file_manager, tmp_path):
        target_file = tmp_path / "important_data.txt"
        original_data = "This is some important data."
        target_file.write_text(original_data)

        with patch('os.replace') as mock_replace:
            mock_replace.side_effect = OSError("Simulated replace failure")

            result = file_manager.atomic_write(file_path=target_file, data="New data that won't be written.")
            assert not result.success, "Atomic write unexpectedly succeeded despite replace failure."
            assert target_file.read_text() == original_data, "Original data was altered despite atomic write failure."

    def test_create_directory(self, file_manager, tmp_path):
        """Test creating a directory"""
        new_dir = tmp_path / "new_test_directory"
        
        result = file_manager.create_directory(dir_path=new_dir)
        assert result.success, f"Create directory failed: {result.error}"
        assert new_dir.exists() and new_dir.is_dir(), "Directory was not created"
    
    def test_create_nested_directory(self, file_manager, tmp_path):
        """Test creating nested directories"""
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        
        result = file_manager.create_directory(dir_path=nested_dir)
        assert result.success, f"Create nested directory failed: {result.error}"
        assert nested_dir.exists() and nested_dir.is_dir(), "Nested directory was not created"
    
    def test_exist_method(self, file_manager, tmp_path):
        """Test the exist method"""
        # Test with existing file
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("test")
        
        result = file_manager.exist(path=existing_file)
        assert result.success, f"Exist check failed: {result.error}"
        assert result.data is True, "Exist should return True for existing file"
        
        # Test with non-existing file
        non_existing = tmp_path / "non_existing.txt"
        result = file_manager.exist(path=non_existing)
        assert result.success, f"Exist check failed: {result.error}"
        assert result.data is False, "Exist should return False for non-existing file"
    
    def test_read_json_invalid_extension(self, file_manager, tmp_path):
        """Test reading JSON from non-JSON file"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text('{"key": "value"}')
        
        result = file_manager.read_json(file_path=txt_file)
        assert not result.success, "Reading JSON from .txt should fail"
    
    def test_delete_nonexistent_file(self, file_manager, tmp_path):
        """Test deleting non-existent file"""
        nonexistent = tmp_path / "does_not_exist.txt"
        
        result = file_manager.delete_file(file_path=nonexistent)
        assert not result.success, "Deleting non-existent file should fail"
    
    def test_delete_nonexistent_directory(self, file_manager, tmp_path):
        """Test deleting non-existent directory"""
        nonexistent = tmp_path / "does_not_exist_dir"
        
        result = file_manager.delete_directory(dir_path=nonexistent)
        assert not result.success, "Deleting non-existent directory should fail"
    
    def test_delete_file_as_directory(self, file_manager, tmp_path):
        """Test deleting a file using delete_directory"""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        
        result = file_manager.delete_directory(dir_path=test_file)
        assert not result.success, "Deleting file as directory should fail"
    
    def test_read_file_as_bytes(self, file_manager, tmp_path):
        """Test reading file as bytes"""
        test_file = tmp_path / "bytes_test.bin"
        test_data = b'\x00\x01\x02\x03\x04'
        test_file.write_bytes(test_data)
        
        result = file_manager.read_file(file_path=test_file, as_bytes=True)
        assert result.success, f"Reading file as bytes failed: {result.error}"
        assert result.data == test_data, "Byte data mismatch"
    
    def test_atomic_write_bytes(self, file_manager, tmp_path):
        """Test atomic write with bytes data"""
        test_file = tmp_path / "bytes_write_test.bin"
        test_data = b'\xff\xfe\xfd\xfc'
        
        result = file_manager.atomic_write(file_path=test_file, data=test_data)
        assert result.success, f"Atomic write bytes failed: {result.error}"
        assert test_file.read_bytes() == test_data, "Written byte data mismatch"
    
    def test_list_of_files_empty_directory(self, file_manager, tmp_path):
        """Test listing files in empty directory"""
        empty_dir = tmp_path / "empty_dir"
        empty_dir.mkdir()
        
        result = file_manager.list_of_files(dir_path=empty_dir, extensions=[], only_name=True)
        assert result.success, f"Listing empty directory failed: {result.error}"
        assert len(result.data) == 0, "Empty directory should have no files"
    
    def test_write_json_with_unicode(self, file_manager, tmp_path):
        """Test writing JSON with unicode characters"""
        test_file = tmp_path / "unicode.json"
        test_data = {"한글": "테스트", "emoji": "🎉", "special": "äöü"}
        
        write_result = file_manager.write_json(file_path=test_file, data=test_data)
        assert write_result.success, f"Write JSON with unicode failed: {write_result.error}"
        
        read_result = file_manager.read_json(file_path=test_file)
        assert read_result.success, f"Read JSON with unicode failed: {read_result.error}"
        assert read_result.data == test_data, "Unicode data mismatch"


if __name__ == "__main__":
    pytest.main([__file__, "-vv"])