from django.db import models
from django.conf import settings


class Document(models.Model):
    ''''''

    title = models.CharField(max_length = 255)
    body = models.TextField()
    text = models.TextField()
    tags = models.TextField()
    label = models.BooleanField()


class Chat(models.Model):
    '''Representa uma conversa entre o usuário e a IA.'''

    id = models.AutoField(primary_key = True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'chats'
    )
    name = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'Chat {self.id} - User {self.user.email}'
    

class Message(models.Model):
    '''Representa uma mensagem dentro de um chat.'''

    id = models.AutoField(primary_key = True)
    chat = models.ForeignKey(
        Chat,
        on_delete = models.CASCADE,
        related_name = 'messages'
    )
    text = models.TextField()
    is_user = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'Message {self.id} - {self.is_user} - Chat {self.chat.id}'


class TaskStatus(models.Model):
    '''Class for modeling TaskStatus (model training status) table on database.'''

    task_id = models.CharField(max_length = 255, unique = True)
    status = models.CharField(max_length = 50)
    result = models.TextField(null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"Task {self.task_id} - Status: {self.status}"