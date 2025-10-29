from enum import Enum

class EnumUtils:
    @staticmethod
    def parse_enum(enum_class: type[Enum], value: str) -> Enum:
        """
        Convert a string into an Enum member.
        Raises ValueError if the value is invalid.
        """
        try:
            return enum_class(value)
        except ValueError:
            raise ValueError(f"'{value}' is not a valid {enum_class.__name__}")
