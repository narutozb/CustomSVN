class MyMetaclass(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        print("1. Metaclass __new__")
        print(name,)
        return super().__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **kwargs):
        print("2. Metaclass __init__")
        super().__init__(name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        print("3. Metaclass __call__")
        return super().__call__(*args, **kwargs)


class MyClass(metaclass=MyMetaclass):
    def __new__(cls, *args, **kwargs):
        print("4. Class __new__ MyClass")
        instance = super().__new__(cls)
        print('4.1 after Class __new__ ')
        return instance

    def __init__(self, value):
        print("5. Class __init__")
        self.value = value

    def __getattribute__(self, name):
        print(f"6. Class __getattribute__: {name}")
        return super().__getattribute__(name)

    def __getattr__(self, name):
        print(f"7. Class __getattr__: {name}")
        return f"Default: {name}"

    def __setattr__(self, name, value):
        print(f"8. Class __setattr__: {name} = {value}")
        super().__setattr__(name, value)

    def __delattr__(self, name):
        print(f"9. Class __delattr__: {name}")
        super().__delattr__(name)

    def __call__(self):
        print("10. Class __call__")
        return self.value

    def __del__(self):
        print("11. Class __del__")


# 使用示例
print("Creating class instance:")
obj = MyClass(42)

print("\nAccessing existing attribute:")
print(obj.value)

print("\nSetting new attribute:")
obj.new_attr = 10

print("\nAccessing non-existent attribute:")
print(obj.non_existent)

print("\nCalling instance as function:")
result = obj()

print("\nDeleting attribute:")
del obj.new_attr

print("\nDeleting instance:")
del obj
