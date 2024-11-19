class BaseTypeCheck:
    def __init__(self) -> None:
        pass
    @staticmethod
    def is_list(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not isinstance(obj, list):
                raise ValueError(f"Expected a list but got {type(obj)}")

        return isinstance(obj, list)
    
    @staticmethod
    def is_dict(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not isinstance(obj, dict):
                raise ValueError(f"Expected a dict but got {type(obj)}")

        return isinstance(obj, dict)

    @staticmethod
    def is_str(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not isinstance(obj, str):
                raise ValueError(f"Expected a str but got {type(obj)}")

        return isinstance(obj, str)

    @staticmethod
    def is_int(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not isinstance(obj, int):
                raise ValueError(f"Expected a int but got {type(obj)}")

        return isinstance(obj, int)
    
    @staticmethod
    def is_float(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not isinstance(obj, float):
                raise ValueError(f"Expected a float but got {type(obj)}")

        return isinstance(obj, float)
    
    @staticmethod
    def is_bool(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not isinstance(obj, bool):
                raise ValueError(f"Expected a bool but got {type(obj)}")

        return isinstance(obj, bool)
    
    @staticmethod
    def is_none(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not obj is None:
                raise ValueError(f"Expected a None but got {type(obj)}")

        return obj is None
    
    @staticmethod
    def is_tuple(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not isinstance(obj, tuple):
                raise ValueError(f"Expected a tuple but got {type(obj)}")

        return isinstance(obj, tuple)
    
    @staticmethod
    def is_set(self, obj: any, error_raise:bool= False) -> bool:
        if error_raise:
            if not isinstance(obj, set):
                raise ValueError(f"Expected a set but got {type(obj)}")

        return isinstance(obj, set)
    
    