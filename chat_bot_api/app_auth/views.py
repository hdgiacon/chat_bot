import traceback

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed, ParseError

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from user.models import CustomUser
from core.models import LogSystem


class CustomTokenObtainPairView(TokenObtainPairView):
    '''Class for login and getting both access and refresh tokens for authentication. Entends `TokenObtainPairView`.'''

    def post(self, request: Request, *args, **kwargs) -> Response:
        '''
        Call post HTTP verb and return both access and refresh tokens for authentication.

        Args:
            request: object for getting client data.

        Return:
            A response object with login success of failure message.
        '''

        try:
            username = request.data.get('username')

            if not username:
                raise AuthenticationFailed('Username must not be empty')

            if not CustomUser.objects.filter(username = username).exists():
                raise AuthenticationFailed('No active account found with the given username')
            
            if not request.data.get('password'):
                raise AuthenticationFailed('Password must not be empty')
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == status.HTTP_200_OK:
                request.session['access_token'] = response.data['access']

            return response

        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status = status.HTTP_401_UNAUTHORIZED)

        except ParseError as e:
            return Response({'error': 'Bad request'}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on user read: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LogoutView(APIView):
    '''Class for logging out and send current token to BlackList. Extends `APIView`.'''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request: Request) -> Response:
        '''
        Call post HTTP verb to logout using refresh token.
        
        Args:
            object for getting client data.

        Return:
            A Response object with logout success or failure message.
        '''

        try:
            refresh_token = request.data["refresh"]
            
            token = RefreshToken(refresh_token)
            
            token = OutstandingToken.objects.get(token = token)
            BlacklistedToken.objects.create(token = token)
            
            return Response({'message': 'Successful logout.'}, status = status.HTTP_204_NO_CONTENT)
        
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on user list: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CustomTokenRefreshView(TokenRefreshView):
    '''Class for access refresh token by token refresh. Extends `TokenRefreshView`. No needed permissions or authentications.'''

    permission_classes = (AllowAny,)