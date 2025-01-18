from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.middleware import csrf
from django.conf import settings
from rest_framework_simplejwt import tokens, views as jwt_views, serializers as jwt_serializers, exceptions as jwt_exceptions
from rest_framework import exceptions as rest_exceptions, response, decorators as rest_decorators, permissions as rest_permissions
from rest_framework_simplejwt.exceptions import TokenError

from account.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer,UserProfileSerializer
from account.renderers import UserRenderer
from account.models import User,UserProfile

from asgiref.sync import sync_to_async
import asyncio

def get_tokens_for_user(user):
  """
    Generate JWT tokens for a given user.

    This function generates a pair of JWT tokens (refresh and access) for the specified user.
    The tokens are created using the `RefreshToken` class, which is typically part of a JWT 
    authentication library such as `djangorestframework-simplejwt`.

    Args:
        user (User): The user instance for whom the tokens are to be generated.

    Returns:
        dict: A dictionary containing the following keys:
            - 'refreshToken' (str): The refresh token as a string.
            - 'accessToken' (str): The access token as a string.
    """
  refresh = RefreshToken.for_user(user)
  return {
      'refreshToken': str(refresh),
      'accessToken': str(refresh.access_token),
  }


class UserRegistrationView(APIView):
  """
    Handle user registration requests.

    This view handles the registration of new users. It processes the incoming POST request,
    validates the user data, creates a new user and user profile, and generates JWT tokens for
    the authenticated session.

    Attributes:
        renderer_classes (list): Specifies the renderer classes to be used for the response.
                                 In this case, it uses `UserRenderer`.

    Methods:
        post(request, format=None):
            Handles the POST request to register a new user.
  """
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    """
        Handle POST request for user registration.

        This method processes the incoming registration data, validates it, creates a new user
        and user profile, and generates JWT tokens for the user. If the data is valid, it returns
        a response with the user profile data and a status of 201 (Created). If the data is invalid,
        it returns a response with the validation errors and a status of 400 (Bad Request).

        Args:
            request (Request): The HTTP request object containing the registration data.
            format (str, optional): The format of the request data. Defaults to None.

        Returns:
            Response: A response object containing the user profile data and JWT tokens if the
                      registration is successful, or validation errors if the registration fails.
    """
    request.data['password2'] = request.data['password']
    request.data['userType'] = 'user'
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
      user = serializer.save()
      requestUserProfile = UserProfile.objects.create(user=user)
      token = get_tokens_for_user(user)
      context = {'token':token}
      serializer = UserProfileSerializer(requestUserProfile,context=context)
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
      errors = []
      for field, error_list in serializer.errors.items():
          for error in error_list:
              errors.append(f"{error}")
      return Response({'errors': errors[0]}, status=status.HTTP_400_BAD_REQUEST)

from datetime import timedelta

class UserLoginView(APIView):
  """
    Handle user login requests.

    This view handles the authentication of users. It processes the incoming POST request,
    validates the user credentials, and generates JWT tokens for the authenticated session.
    It also sets the authentication cookies in the response.

    Attributes:
        renderer_classes (list): Specifies the renderer classes to be used for the response.
                                 In this case, it uses `UserRenderer`.

    Methods:
        post(request, format=None):
            Handles the POST request to authenticate a user.
    """
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    """
        Handle POST request for user login.

        This method processes the incoming login data, validates it, authenticates the user,
        and generates JWT tokens for the user. If the credentials are valid, it returns a response
        with the user profile data and sets the authentication cookies. If the credentials are invalid,
        it returns a response with an error message and a status of 404 (Not Found).

        Args:
            request (Request): The HTTP request object containing the login data.
            format (str, optional): The format of the request data. Defaults to None.

        Returns:
            Response: A response object containing the user profile data and JWT tokens if the
                      authentication is successful, or an error message if the authentication fails.
      """
    if not request.data.get('portal') or request.data.get('email') == None or request.data.get('password') == None:
      return Response({'message':'Please provide email and password'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = UserLoginSerializer(data=request.data)
    portal = request.data.get('portal')
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)

    if user is not None:
      if user.userType == 'superAdmin' and portal != 'admin':
        return Response({'message':'You are not authorized to login in this portal'}, status=status.HTTP_404_NOT_FOUND)
      elif user.userType == 'user' and portal != 'user':
        return Response({'message':'You are not authorized to login in this portal'}, status=status.HTTP_404_NOT_FOUND)
      
      token = get_tokens_for_user(user)
      userProfile = UserProfile.objects.select_related('user').only(
                'id', 'user__id', 'user__name', 'user__email', 'user__userType', 'profilePic'
            ).get(user=user)
      serializer = UserProfileSerializer(userProfile,context={'token':token})
      response = Response(serializer.data, status=status.HTTP_200_OK)
      response.set_cookie(
              key=settings.SIMPLE_JWT['AUTH_COOKIE'],
              value=token["accessToken"],
              # expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
              # expires=timedelta(minutes=5),
              secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
              httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
              samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
          )
      response.set_cookie(
              key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
              value=token["refreshToken"],
              # expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
              secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
              httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
              samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
          )
      response["X-CSRFToken"] = csrf.get_token(request)
      return response
    else:
      return Response({'message': 'Email or Password is not Valid'}, status=status.HTTP_404_NOT_FOUND)

# this code was being used for http only cookies 
# @api_view(['POST'])
# def refreshToken(request):
#     try:
#         refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
#         accessToken = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
#         if not refresh_token:
#             return Response({'error': 'Refresh token is missing'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             refresh = RefreshToken(refresh_token)
#             new_access_token = str(refresh.access_token)
#             new_refresh_token = str(refresh)
#             user = User.objects.get(id=refresh['user_id'])
#             userProfile = UserProfile.objects.get(user=user)
#             context = {'token': {'accessToken':new_access_token, 'refreshToken':new_refresh_token}}
#             serializer = UserProfileSerializer(userProfile,context=context)

#             response = Response(serializer.data, status=status.HTTP_200_OK)
#             response.set_cookie(
#                 key=settings.SIMPLE_JWT['AUTH_COOKIE'],
#                 value=new_access_token,
#                 expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
#                 secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
#                 httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
#                 samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
#             )
#             response.set_cookie(
#                 key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
#                 value=new_refresh_token,
#                 expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
#                 secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
#                 httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
#                 samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
#             )
#             return response
#         except TokenError as e:
#             return Response({'error': 'Invalid refresh token'}, status=status.HTTP_403_FORBIDDEN)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def refreshToken(request):
    refresh = request.data.get('refreshToken')
    if not refresh:
        return Response({'message': 'Refresh token is required'}, status=400)

    try:
        refreshToken = RefreshToken(refresh)
        accessToken = str(refreshToken.access_token)
        userInstance = User.objects.get(id=refreshToken.payload.get('user_id'))
        requestUserProfile = UserProfile.objects.filter(user=userInstance).first()
        tokens ={
            'accessToken': str(accessToken),
            'refreshToken': str(refreshToken)
        }
        serializer = UserProfileSerializer(requestUserProfile,context={'token':tokens})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_403_FORBIDDEN)
    

@api_view(['POST'])
def logoutView(request): 
    try:
        refreshToken = request.COOKIES.get(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        token = tokens.RefreshToken(refreshToken)
        ## blacklisting the refresh token if user logout
        try:
           token.blacklist()
        except Exception as e:
            print('-----------------exception in blacklisting token',e)
            pass
        # token.blacklist()

        res = response.Response()
        res.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        res.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        res.delete_cookie("X-CSRFToken")
        res.delete_cookie("csrftoken")
        res["X-CSRFToken"]=None
        res.data = {'msg': 'Logout Success'}
        res.status_code = status.HTTP_200_OK
        return res
    except Exception as e:
        res = response.Response()
        res.data = {'msg': 'Logout Failed'}
        res.status_code = status.HTTP_400_BAD_REQUEST
        return res


class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)


class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UserPasswordResetView(request):
  password = request.data.get('password')
  password2 = request.data.get('password2')
  if password != password2:
    return Response({'message':'Password and Confirm Password doesn\'t match'}, status=status.HTTP_400_BAD_REQUEST)
  user = User.objects.get(id=request.user.id)
  user.set_password(password)
  user.save()
  token = get_tokens_for_user(user)
  requestUserProfile = UserProfile.objects.get(user=user)
  serializer = UserProfileSerializer(requestUserProfile,context={'token':token})  
  return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllUsers(request):
    requestUserProfile = UserProfile.objects.get(user=request.user)
    if requestUserProfile.user.userType != 'superAdmin':
        return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    users = UserProfile.objects.all()
    accessToken = ""
    refreshToken = ""
    context = {'token': {'accessToken':accessToken, 'refreshToken':refreshToken}}
    serializer = UserProfileSerializer(users, many=True,context=context)
    return Response(serializer.data, status=status.HTTP_200_OK)



@rest_decorators.api_view(["GET"])
@permission_classes([IsAuthenticated])
def checkValidSession(request):
    return Response({"valid": True}, status=status.HTTP_200_OK)
    