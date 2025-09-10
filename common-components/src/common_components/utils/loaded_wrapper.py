from functools import wraps


def loaded_first(need_data: bool = True):
    """Decorator factory that ensures the telco directory is loaded and has data before method execution.

    Args:
        need_data: Whether to check if data exists (default: True).

    Returns:
        The decorator function that checks for loaded state and optionally data existence.

    Raises:
        RuntimeError: If the telco directory is not loaded or data is None (when need_data=True).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.loaded:
                raise RuntimeError("Telco directory not loaded. Please call load() first.")
            if need_data and self.data is None:
                raise RuntimeError("Telco directory data is None. Please ensure data is properly loaded.")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
