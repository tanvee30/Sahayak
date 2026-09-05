import random
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import EmailOTP


def generate_otp_code():
    return f"{random.randint(100000, 999999)}"


# def create_and_send_otp(email, purpose="signup"):
#     code = generate_otp_code()
#     otp = EmailOTP.objects.create(
#         email=email,
#         code=code,
#         purpose=purpose,
#         expires_at=timezone.now() + timedelta(minutes=10),
#     )
#     send_mail(
#         subject=f"Your Sahayak {purpose} OTP",
#         message=f"Your OTP code is: {code}. It expires in 10 minutes.",
#         from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
#         recipient_list=[email],
#         fail_silently=False,
#     )
#     return otp
def create_and_send_otp(email, purpose="signup"):
    code = generate_otp_code()

    otp = EmailOTP.objects.create(
        email=email,
        code=code,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=10),
    )

    send_mail(
        subject="Your Sahayak OTP Verification Code",
        message=(
            f"Your OTP is: {code}\n\n"
            "This OTP is valid for 10 minutes.\n"
            "Please do not share this OTP with anyone."
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    return otp