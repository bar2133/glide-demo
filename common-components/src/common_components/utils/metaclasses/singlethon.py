class Singleton(type):
    """Metaclass that implements the Singleton design pattern.

    This metaclass ensures that only one instance of a class can exist at any time.
    When a class uses this metaclass, subsequent instantiation attempts will return
    the same instance that was created during the first instantiation.

    The singleton instances are stored in a class-level dictionary where the key
    is the class itself and the value is the single instance of that class.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Control the instantiation of classes using this metaclass.

        This method is called when an instance of a class using this metaclass
        is created. It checks if an instance already exists for the class, and
        if not, creates one. Otherwise, it returns the existing instance.

        Args:
            *args: Variable length argument list passed to the class constructor.
            **kwargs: Arbitrary keyword arguments passed to the class constructor.

        Returns:
            The single instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
