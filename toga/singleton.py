class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:

        # usage of class that is child of Singleton

        >>> from toga.toga_settings import Settings
        >>> a = Settings()
        >>> b = Settings()
        >>> assert a is b
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
