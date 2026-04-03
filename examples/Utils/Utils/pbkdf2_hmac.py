from pathlib import Path
from tbot223_core import Utils

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize Utils
    utils = Utils(is_logging_enabled=True, base_dir=BASE_DIR)

    # Generate PBKDF2-HMAC hash
    hash_info = utils.pbkdf2_hmac(
        password="my_secure_password",
        algorithm="sha256",
        iterations=100000,
        salt_size=16
    )
    print("Hash info:", hash_info.data)

    # Verify with correct password
    verify_ok = utils.verify_pbkdf2_hmac(
        password="my_secure_password",
        salt_hex=hash_info.data["salt_hex"],
        hash_hex=hash_info.data["hash_hex"],
        iterations=hash_info.data["iterations"],
        algorithm=hash_info.data["algorithm"]
    )
    print("Correct password:", verify_ok.data)

    # Verify with wrong password
    verify_fail = utils.verify_pbkdf2_hmac(
        password="wrong_password",
        salt_hex=hash_info.data["salt_hex"],
        hash_hex=hash_info.data["hash_hex"],
        iterations=hash_info.data["iterations"],
        algorithm=hash_info.data["algorithm"]
    )
    print("Wrong password:", verify_fail.data)

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
