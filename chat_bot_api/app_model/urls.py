from django.urls import path
from .views import SendDatabaseAndTrainModel, TrainTaskStatusView, SearchInformationView, CreateChatView, ListChatView, DeleteChatView, CreateMessageView, ListMessagesView

app_name = 'app_model'

urlpatterns = [
    path('train/model/', SendDatabaseAndTrainModel.as_view(), name = 'send-database'),
    path('monitor/training/', TrainTaskStatusView.as_view(), name = 'task-status'),
    path('search/information/', SearchInformationView.as_view(), name = 'search-information'),
    path('chat/create/', CreateChatView.as_view(), name = 'create-chat'),
    path('chat/list/', ListChatView.as_view(), name = 'list-chat'),
    path('chat/<int:pk>/delete/', DeleteChatView.as_view(), name = 'delete-chat'),
    path('message/<int:chat_id>/create/', CreateMessageView.as_view(), name = 'message-create'),
    path('message/<int:chat_id>/list/', ListMessagesView.as_view(), name = 'message-list'),
]