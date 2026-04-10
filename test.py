from tbot223_core.AppCore import AppCore

if __name__ == "__main__":
    # Example usage of AppCore with DefaultInit
    app_core = AppCore()
    app_core._log("INFO", "This is a test log message from AppCore.")

    check_attr = {
        "_is_logging_enabled": True,
        "_is_debug_enabled": True,
        "_logger_manager": None,
        "log": None,
        "logger": None,
        "_log": None,
        "_exception_tracker": None
    }

    for attr, expected in check_attr.items():
        actual = getattr(app_core, attr, None)
        print(f"{attr}: {actual} (Expected: {expected})")