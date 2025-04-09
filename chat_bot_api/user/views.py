import traceback
from django.http import Http404

from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed, ValidationError, ParseError
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import LogSystem

from .models import CustomUser
from .serializers import UserCreateSerializer, UserListSerializer, UserReadSerializer, UserUpdateSerializer


class IsStaffUser(BasePermission):
    '''is_staff class for validating permission. Extends `BasePermission`.'''

    def has_permission(self, request: Request, view):
        '''
        Verify if current user has `staff` permission role.

        Args:
            request: object for getting client data.

        Returns:
            if is staff user or not.
        '''
        
        return request.user and request.user.is_staff


class UserCreate(generics.CreateAPIView):
    '''Class for creating a new user and saving on Postgre database. Extends `CreateAPIView`.'''
    
    queryset = CustomUser.objects.all()
    serializer_class = UserCreateSerializer
    
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def create(self, request: Request) -> Response:
        '''
        Create a new CustomUser and verify if is validated.

        Args:
            request: object for getting client data.

        Return:
            A Response object with success or failure message.
        '''

        try:
            serializer = self.get_serializer(data = request.data)

            serializer.is_valid(raise_exception = True)

            user = serializer.save()

            headers = self.get_success_headers(serializer.data)
            
            return Response({'message': 'User created successfully'}, status = status.HTTP_201_CREATED, headers = headers)

        except ValidationError as e:
            error_message = next(iter(e.detail.values()))[0]
            
            return Response({'error': error_message}, status = status.HTTP_400_BAD_REQUEST)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())
            
            return Response({'error on user create: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserList(generics.ListAPIView):
    '''Class for listing all CustomUser on database. Extends `ListAPIView`.'''
    
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    
    permission_classes = (IsAuthenticated, IsStaffUser)
    authentication_classes = (JWTAuthentication,)

    def list(self, request: Request, *args, **kwargs) -> Response:
        '''
        List all CustomUser's as list and Verify if current user is authenticated.

        Args:
            request: object for getting client data.

        Return:
            A Response object with success or failure message.
        '''

        try:
            return super().list(request, *args, **kwargs)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on user list: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserRead(generics.RetrieveAPIView):
    '''Class for read a user data by it's id. Extends `RetrieveAPIView`.'''
    
    queryset = CustomUser.objects.all()
    serializer_class = UserReadSerializer
    
    permission_classes = [IsAuthenticated, IsStaffUser]

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        '''
        Read a user based on CustomUser id. Muste be authenticated.

        Args:
            request: object for getting client data.

        Return:
            A Response object with CustomUser data or `AuthenticationFailed`, `Http404` exceptions.
        '''

        try:
            return super().retrieve(request, *args, **kwargs)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except Http404:
            return Response({'error': 'User not found'}, status = status.HTTP_404_NOT_FOUND)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on user read: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserUpdate(generics.UpdateAPIView):
    '''Class for update a user data by it's id. Extends `RetrieveAPIView`.'''
    
    queryset = CustomUser.objects.all()

    serializer_class = UserUpdateSerializer
    
    permission_classes = [IsAuthenticated, IsStaffUser]

    def update(self, request: Request, *args, **kwargs) -> Response:
        '''
        Update a user based on CustomUser id. Muste be authenticated and fields will be validated.

        Args:
            request: object for getting client data.

        Return:
            A Response object with CustomUser data or `AuthenticationFailed`, `Http404`, `ValidationError` exceptions.
        '''

        try:
            instance = self.get_object()

            serializer = self.get_serializer(instance, data = request.data)
            serializer.is_valid(raise_exception = True)
            
            self.perform_update(serializer)
            
            return Response({'message': 'User updated successfully'}, status = status.HTTP_201_CREATED)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except Http404:
            return Response({'error': 'User not found'}, status = status.HTTP_404_NOT_FOUND)

        except ValidationError:
            return Response({'error': 'Validation failed'}, status = status.HTTP_400_BAD_REQUEST)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on user read: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserDelete(generics.DestroyAPIView):
    '''Class for delete a user data by it's id. Extends `RetrieveAPIView`.'''
    
    queryset = CustomUser.objects.all()
    serializer_class = UserReadSerializer
    
    permission_classes = [IsAuthenticated, IsStaffUser]

    def destroy(self, request: Request, *args, **kwargs):
        '''
        Delete a user based on CustomUser id. Muste be authenticated.

        Args:
            request: object for getting client data.

        Return:
            A Response object with CustomUser data or `AuthenticationFailed`, `Http404` exceptions.
        '''

        try:
            return super().destroy(request, *args, **kwargs)
        
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except Http404:
            return Response({'error': 'User not found'}, status = status.HTTP_404_NOT_FOUND)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on user read: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)