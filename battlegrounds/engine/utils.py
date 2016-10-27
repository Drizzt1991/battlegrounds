
def lazy_property(fn):
    def getter(self):
        value = fn(self)
        # Cache it for further access. By using the same name as our property
        # we avoid further call of this function, as __getattr__ will just
        # use the value in object's __dict__
        self.__dict__[fn.__name__] = value
        return value
    return property(getter)
