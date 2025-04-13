from django.urls import path
from .views import SendDatabaseAndTrainModel, TrainTaskStatusView

urlpatterns = [
    path('train/model/', SendDatabaseAndTrainModel.as_view(), name = 'send-database'),
    path('monitor/training/', TrainTaskStatusView.as_view(), name = 'task-status'),
]