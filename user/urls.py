from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from user.views import CreateUserView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
]

app_name = "user"
