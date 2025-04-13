from django.db import models


class Document(models.Model):

    title = models.CharField(max_length = 255)
    body = models.TextField()
    text = models.TextField()
    tags = models.TextField()
    label = models.BooleanField()


class TaskStatus(models.Model):
    '''Class for modeling TaskStatus (model training status) table on database.'''

    task_id = models.CharField(max_length = 255, unique = True)
    status = models.CharField(max_length = 50)
    result = models.TextField(null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"Task {self.task_id} - Status: {self.status}"