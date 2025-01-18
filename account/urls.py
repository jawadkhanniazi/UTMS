from django.urls import path
from account.views import (SendPasswordResetEmailView, 
                           UserChangePasswordView, 
                           UserLoginView, 
                           UserProfileView, 
                           UserRegistrationView, 
                           getAllUsers,
                           UserPasswordResetView,
                           logoutView,
                           refreshToken,
                           checkValidSession
                        )

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('refresh/', refreshToken, name='refreshToken'),
    path('logout/', logoutView, name='logout'),
    path('users/',getAllUsers, name='users'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/', UserPasswordResetView, name='reset-password'),
    path('checkValidSession/', checkValidSession, name='test'),
]