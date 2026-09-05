from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", views.ResendOTPView.as_view(), name="resend-otp"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("select-role/", views.SelectRoleView.as_view(), name="select-role"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("me/", views.MeView.as_view(), name="me"),
]