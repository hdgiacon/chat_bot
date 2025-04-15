from django.db import models

class LogSystem(models.Model):
    '''Class for log support when HTTP 500 error accurs and save on database. Has error message and create timestamp.'''

    class Meta:
        app_label = 'core'

    error = models.TextField()
    stacktrace = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
