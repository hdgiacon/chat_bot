import os
import traceback
import shutil

from django.conf import settings
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed, ValidationError, ParseError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import LogSystem
from .models import TaskStatus
from .tasks import set_database_and_train_data, get_response_from_vector_base
from .services import ChatService, MessageService


class SendDatabaseAndTrainModel(APIView):
    parser_classes = (MultiPartParser, FormParser)

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    
    def post(self, _: Request) -> Response:
        ''''''

        download_dir = settings.MEDIA_ROOT
        
        try:
            if not os.path.exists(download_dir):
                task = set_database_and_train_data.delay(download_dir)
                
                return Response({"message": "Training started successfully.", "task_id": task.id}, status = status.HTTP_201_CREATED)
            
            return Response({"message": "Model already trained"}, status = status.HTTP_200_OK)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)

        except ValidationError as e:
            error_message = next(iter(e.detail.values()))[0]

            return Response({"error": error_message}, status = status.HTTP_400_BAD_REQUEST)
        
        except ParseError as e:
            return Response({'error': 'Bad request'}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            if os.path.exists(download_dir):
                shutil.rmtree(download_dir)

            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({"error": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TrainTaskStatusView(APIView):
    '''View to query the status of a specific task by task_id.'''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request: Request) -> Response:
        '''
        Call post HTTP verb and return current SendLawDatabaseAndTrainModel asynchronous status.

        Args:
            request: object for getting client data.

        Return:
            A response object with training current status.
        '''

        try:
            task_status = TaskStatus.objects.filter(task_id = request.data.get('task_id')).first()
            
            if task_status:
                return Response(
                    {
                        'task_id': task_status.task_id,
                        'status': task_status.status,
                        'result': task_status.result,
                        'created_at': task_status.created_at,
                        'updated_at': task_status.updated_at,
                    }, 
                    status = status.HTTP_200_OK
                )
            
            else:
                raise ValidationError('No task found for this task_id.')
            
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)

        except ValidationError as e:
            error_message = next(iter(e.detail.values()))[0]

            return Response({"error": error_message}, status = status.HTTP_404_NOT_FOUND)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SearchInformationView(APIView):
    '''View for sendind an question or sentence and getting an answer based on Sentece Similarity.'''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request: Request) -> Response:
        '''
        Call post HTTP verb and return a message with question or sentence passed on body endpoint answer.

        Args:
            request: object for getting client data.

        Return:
            A response object with Sentence SImilarity response.
        '''

        try:
            question = request.data.get('prompt', None)

            model_response = get_response_from_vector_base(question)

            return Response(model_response, status = status.HTTP_200_OK)
        
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except ValidationError as e:
            error_message = next(iter(e.detail.values()))[0]

            return Response({'error': error_message}, status = status.HTTP_400_BAD_REQUEST)
        
        except ParseError as e:
            return Response({'error': 'Bad request'}, status = status.HTTP_400_BAD_REQUEST)
        
        except (ValueError, FileNotFoundError) as e:
            return Response({'error': str(e)}, status = status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on process sentence: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CreateChatView(APIView):
    ''''''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request: Request) -> Response:
        ''''''

        try:
            chat = ChatService.create(request)

            return Response(chat, status = status.HTTP_201_CREATED)

        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)

        except ValidationError as e:
            error_message = next(iter(e.detail.values()))[0]

            return Response({"error": error_message}, status = status.HTTP_404_NOT_FOUND)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListChatView(APIView):
    ''''''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request: Request) -> Response:
        ''''''
        
        try:
            chat_data = ChatService.list_chats(request)
            
            return Response(chat_data, status = status.HTTP_200_OK)
        
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on chat list: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DeleteChatView(APIView):
    ''''''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def delete(self, request: Request, pk: int) -> Response:
        ''''''
        
        try:
            chat_name = ChatService.delete(request, pk)

            return Response({'message': f'{chat_name} deleted succesfully.'}, status = status.HTTP_204_NO_CONTENT)
        
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except Http404:
            return Response({'error': 'Chat not found'}, status = status.HTTP_404_NOT_FOUND)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on chat delete: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CreateMessageView(APIView):
    ''''''
    
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request: Request, chat_id: int) -> Response:
        ''''''
        
        try:
            message = MessageService.create(request, chat_id)

            return Response(message, status = status.HTTP_201_CREATED)
        
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)

        except ValidationError as e:
            error_message = next(iter(e.detail.values()))[0]

            return Response({"error": error_message}, status = status.HTTP_404_NOT_FOUND)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListMessagesView(APIView):
    ''''''

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, _: Request, chat_id: int) -> Response:
        ''''''

        try:
            message_data = MessageService.list_messages(chat_id)

            return Response(message_data, status = status.HTTP_200_OK)
        
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed.'}, status = status.HTTP_401_UNAUTHORIZED)
        
        except ParseError as e:
            return Response({'error': str(e)}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

            return Response({'error on chat list: ': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)