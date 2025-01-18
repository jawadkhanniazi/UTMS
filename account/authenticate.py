from rest_framework_simplejwt import authentication as jwt_authentication
from django.conf import settings
from rest_framework import authentication, exceptions as rest_exceptions

def enforce_csrf(request):
    check = authentication.CSRFCheck(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise rest_exceptions.PermissionDenied('CSRF Failed: %s' % reason)

class CustomAuthentication(jwt_authentication.JWTAuthentication):
    def authenticate(self, request):
        if request.path.startswith('/admin/'):
            return None
        
        header = self.get_header(request)
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None 

        if header is None and raw_token is None:
            return None
        elif header is not None:
            raw_token = self.get_raw_token(header)
            
        if raw_token is None:
            return None
        
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return user, validated_token
        except Exception as e:
            return None