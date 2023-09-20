from django.utils.translation import ngettext
from django.forms import ValidationError


class MaximumLengthValidator:
    """
    Validate that the password has a minimum number of uppercase letters.
    """

    def __init__(self, max_length=64):
        self.max_length = max_length

    def validate(self, password:str, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                ngettext(
                    "This password is too long. It must contain at most %(max_length)d character.",
                    "This password is too long. It must contain at most %(max_length)d characters.",
                    self.max_length,
                ),
                code="too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self):
        return ngettext(
            "This password is too long. It must contain at most %(max_length)d character.",
            "This password is too long. It must contain at most %(max_length)d characters.",
            self.max_length,
        ) % {"max_length": self.max_length}


class UppercaseValidator:
    """
    Validate that the password has a minimum number of uppercase letters.
    """

    def __init__(self, min_number=2):
        self.min_number = min_number

    def validate(self, password:str, user=None):
        number_of_upper = sum(1 for char in password if char.isupper())
        if number_of_upper < self.min_number:
            raise ValidationError(
                ngettext(
                    "This password must contain at least %(min_number)d uppercase character.",
                    "This password must contain at least %(min_number)d uppercase characters.",
                    self.min_number,
                ),
                code="insufficient_uppercase",
                params={"min_number": self.min_number},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(min_number)d uppercase character.",
            "Your password must contain at least %(min_number)d uppercase characters.",
            self.min_number,
        ) % {"min_number": self.min_number}


class LowercaseValidator:
    """
    Validate that the password has a minimum number of lowercase letters.
    """

    def __init__(self, min_number=2):
        self.min_number = min_number

    def validate(self, password:str, user=None):
        number_of_lower = sum(1 for char in password if char.islower())
        if number_of_lower < self.min_number:
            raise ValidationError(
                ngettext(
                    "This password must contain at least %(min_number)d lowercase character.",
                    "This password must contain at least %(min_number)d lowercase characters.",
                    self.min_number,
                ),
                code="insufficient_lowercase",
                params={"min_number": self.min_number},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(min_number)d lowercase character.",
            "Your password must contain at least %(min_number)d lowercase characters.",
            self.min_number,
        ) % {"min_number": self.min_number}


class NumericValidator:
    """
    Validate that the password has a minimum number of numeric characters.
    """

    def __init__(self, min_number=2):
        self.min_number = min_number

    def validate(self, password:str, user=None):
        number_of_numeric = sum(1 for char in password if char.isnumeric())
        if number_of_numeric < self.min_number:
            raise ValidationError(
                ngettext(
                    "This password must contain at least %(min_number)d numeric character.",
                    "This password must contain at least %(min_number)d numeric characters.",
                    self.min_number,
                ),
                code="insufficient_numeric",
                params={"min_number": self.min_number},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(min_number)d numeric character.",
            "Your password must contain at least %(min_number)d numeric characters.",
            self.min_number,
        ) % {"min_number": self.min_number}
    

class SpecialCharacterValidator:
    """
    Validate that the password has a minimum number of special characters.
    """

    def __init__(self, min_number=2):
        self.min_number = min_number

    def validate(self, password:str, user=None):
        special = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        number_of_numeric = sum(1 for char in password if char in special)
        if number_of_numeric < self.min_number:
            raise ValidationError(
                ngettext(
                    "This password must contain at least %(min_number)d special character.",
                    "This password must contain at least %(min_number)d special characters.",
                    self.min_number,
                ),
                code="insufficient_special",
                params={"min_number": self.min_number},
            )

    def get_help_text(self):
        return ngettext(
            "Your password must contain at least %(min_number)d special character.",
            "Your password must contain at least %(min_number)d special characters.",
            self.min_number,
        ) % {"min_number": self.min_number}
    
