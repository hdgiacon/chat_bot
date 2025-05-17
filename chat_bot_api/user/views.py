import traceback
from django.http import Http404

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed, ValidationError, ParseError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView

from core.models import LogSystem

from .models import CustomUser
from .serializers import UserCreateSerializer, UserListSerializer, UserReadSerializer, UserUpdateSerializer


class UserCreateView(APIView):
    '''Class for creating a new user and saving on PostgreSQL database.'''
    
    permission_classes = (AllowAny,)
    authentication_classes = ()
    
    def post(self, request: Request) -> Response:
        '''
        Handle POST request to create a new CustomUser.

        Args:
            request: object containing client data.

        Returns:
            A Response object with success or error message.
        '''
        
        try:
            serializer = UserCreateSerializer(data = request.data)
            serializer.is_valid(raise_exception = True)
            
            user = serializer.save()

            headers = {'Location': f'/users/{user.id}/'}

            return Response({'message': 'User created successfully'}, status = status.HTTP_201_CREATED, headers = headers)

        except ValidationError as e:
            error_message = next(iter(e.detail.values()))[0]
            
            return Response({'error': error_message}, status = status.HTTP_400_BAD_REQUEST)

        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())
            
            return Response({'error on user create': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(APIView):
    '''Class for listing all CustomUser in the database.'''
    
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, _: Request) -> Response:
        '''
        Handle GET request to list all CustomUser instances.

        Args:
            request: object for getting client data.

        Returns:
            A Response object with serialized user data or error message.
        '''

        try:
            users = CustomUser.objects.all()
            
            serializer = UserListSerializer(users, many = True)
            
            return Response(serializer.data, status = status.HTTP_200_OK)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)

        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())
            
            return Response({'error on user list': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserReadView(APIView):
    '''Class for reading a user's data by ID.'''
    
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, _: Request, pk: int) -> Response:
        '''
        Handle GET request to retrieve a CustomUser by primary key (ID).

        Args:
            request: object for getting client data.
            pk: primary key of the user to retrieve.

        Returns:
            A Response object with the serialized user data or an error message.
        '''
        try:
            user = CustomUser.objects.filter(id = pk).first()
            
            if not user:
                raise Http404

            serializer = UserReadSerializer(user)
            
            return Response(serializer.data, status = status.HTTP_200_OK)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)

        except Http404:
            return Response({'error': 'User not found'}, status = status.HTTP_404_NOT_FOUND)

        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())
            
            return Response({'error on user read': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)        


class UserUpdateView(APIView):
    '''Class for updating a user's data by ID.'''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def put(self, request: Request, pk: int) -> Response:
        '''
        Update a user based on CustomUser id. Must be authenticated and fields will be validated.

        Args:
            request: object for getting client data.
            pk: user ID.

        Return:
            A Response object with a success message or an appropriate error message.
        '''
        try:
            user = CustomUser.objects.filter(id = pk).first()
            
            if not user:
                raise Http404

            serializer = UserUpdateSerializer(user, data = request.data)
            
            serializer.is_valid(raise_exception = True)
            serializer.save()

            return Response({'message': 'User updated successfully'}, status = status.HTTP_200_OK)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)

        except Http404:
            return Response({'error': 'User not found'}, status = status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            error_message = next(iter(e.detail.values()))[0]
            
            return Response({'error': error_message}, status = status.HTTP_400_BAD_REQUEST)

        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())
            
            return Response({'error on user update': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDeleteView(APIView):
    '''Class for deleting a user by its id.'''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, _: Request, pk: int) -> Response:
        '''
        Delete a user based on CustomUser id. Must be authenticated.

        Args:
            request: object for getting client data.
            pk: user ID.

        Return:
            A Response object with success or error message.
        '''
        try:
            user = CustomUser.objects.filter(id = pk).first()
            
            if not user:
                raise Http404

            user.delete()

            return Response({'message': 'User deleted successfully'}, status = status.HTTP_204_NO_CONTENT)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)

        except Http404:
            return Response({'error': 'User not found'}, status = status.HTTP_404_NOT_FOUND)

        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())
            
            return Response({'error on user delete': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)