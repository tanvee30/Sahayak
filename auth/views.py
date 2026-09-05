from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailOTP
from .serializers import (
    SignupSerializer,
    VerifyOTPSerializer,
    LoginSerializer,
    SelectRoleSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from .utils import create_and_send_otp
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.create_user(
            email=data["email"], username=data["username"], password=data["password"]
        )
        user.is_verified = False
        user.save()

        create_and_send_otp(user.email, purpose="signup")
        return Response(
            {"message": "Signup successful. OTP sent to email."},
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        otp = (
            EmailOTP.objects.filter(email=email, code=code, purpose="signup", used=False)
            .order_by("-created_at")
            .first()
        )
        if otp is None:
            return Response({"error": "Invalid or already-used OTP."}, status=status.HTTP_400_BAD_REQUEST)
        if otp.is_expired():
            return Response({"error": "OTP expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        otp.used = True
        otp.save()

        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()

        return Response({"message": "Email verified successfully.", **_tokens_for(user)})


class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No account found for this email."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"message": "This account is already verified."})

        create_and_send_otp(email, purpose="signup")
        return Response({"message": "A new OTP has been sent."})


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_verified:
            return Response({"error": "Please verify your email with the OTP first."}, status=status.HTTP_403_FORBIDDEN)

        return Response(_tokens_for(user))

class SelectRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SelectRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.role = serializer.validated_data["role"]
        user.save(update_fields=["role"])

        return Response({
            "message": "Role selected successfully.",
            "role": user.role,
        })

class ForgotPasswordView(APIView):

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.is_active:
            return Response(
                {"error": "This account is inactive."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_and_send_otp(email, purpose="password_reset")

        return Response({
            "message": "Password reset OTP sent to your email."
        })

class ResetPasswordView(APIView):

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        # Find the latest unused password-reset OTP
        otp = (
            EmailOTP.objects.filter(
                email=email,
                code=code,
                purpose="password_reset",
                used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if otp is None:
            return Response(
                {"error": "Invalid or already-used OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp.is_expired():
            return Response(
                {"error": "OTP expired. Please request a new password reset OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Mark OTP as used
        otp.used = True
        otp.save(update_fields=["used"])

        # Set the new password securely
        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response({
            "message": "Password reset successfully. You can now log in with your new password."
        })

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_verified": user.is_verified,
        })