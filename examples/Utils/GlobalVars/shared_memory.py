import os
from pathlib import Path
from tbot223_core import GlobalVars

# Define base directory
BASE_DIR=Path(__file__).resolve().parents[2] / ".OtherFiles"

if __name__ == "__main__":
    # Initialize two instances to simulate separate processes
    gv_main = GlobalVars(is_logging_enabled=True, base_dir=BASE_DIR)
    gv_child = GlobalVars(is_logging_enabled=False, base_dir=BASE_DIR)

    shm_name = f"example_global_vars_shm_{os.getpid()}"

    # Create shared memory in the owner process
    gen_result = gv_main.shm_gen(name=shm_name, size=4096, create_lock=False)
    if not gen_result.success:
        print("Shared memory creation failed:", gen_result.error)
    else:
        # Store variables and synchronize to shared memory
        gv_main.set("message", "hello shared memory")
        gv_main.set("count", 3)
        sync_result = gv_main.shm_sync(shm_name, serialize_format="json")

        if not sync_result.success:
            print("Shared memory sync failed:", sync_result.error)
        else:
            # Connect from another instance and read values back
            connect_result = gv_child.shm_connect(shm_name)
            if not connect_result.success:
                print("Shared memory connect failed:", connect_result.error)
            else:
                shm_obj = gv_child.shm_get(shm_name)
                print("Shared memory name:", shm_obj.data.name)

                update_result = gv_child.shm_update(shm_name, serialize_format="json")
                if update_result.success:
                    print("message from child:", gv_child.get("message").data)
                    print("count from child:", gv_child.get("count").data)
                else:
                    print("Shared memory update failed:", update_result.error)

                # Child connections should usually use close_only=True.
                gv_child.shm_close(shm_name, close_only=True)

        # The owner process is responsible for unlinking the block.
        gv_main.shm_close(shm_name)

    gv_main.clear()
    gv_child.clear()

    print("\n -------------- \n TEST COMPLETE \n -------------- \n")
