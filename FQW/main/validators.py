from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру.", code="password_no_number")

        if not any(char.islower() for char in password):
            raise ValidationError("Пароль должен содержать хотя бы одну строчную букву.", code="password_no_lower")

        if not any(char.isupper() for char in password):
            raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву.", code="password_no_upper")

        if len(password) < 8:
            raise ValidationError("Пароль должен быть не менее 8 символов.", code="password_too_short")

    def get_help_text(self):
        return "Пароль должен содержать не менее 8 символов, включая строчные и заглавные буквы, а также хотя бы одну цифру."
