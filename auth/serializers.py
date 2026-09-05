from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

# Signup
class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

# Verify OTP
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

# Login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# Role Selection
class SelectRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=User.Role.choices
    )
# Forgot Password
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

# Reset Password
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(
        write_only=True,
        min_length=6
    )

# Logout
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()