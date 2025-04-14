import os
import traceback
import shutil

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from celery import shared_task, states

from .models import TaskStatus
from .services import PrepareDataService, SetDocumentsOnDatabase, GenerateEmbeddings
from core.models import LogSystem


@shared_task
def set_database_and_train_data(download_dir: str):
    ''''''

    try:
        task_id = set_database_and_train_data.request.id

        TaskStatus.objects.get_or_create(
            task_id = task_id,
            defaults = {'status': states.PENDING, 'result': 'Downloading data from HuggingFace'}
        )

        PrepareDataService.get_huggingface_data_and_save(download_dir)

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.PENDING,
            result = 'Setting data on Postgre database'
        )

        SetDocumentsOnDatabase.set_data_on_postgre(download_dir)

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.PENDING,
            result = 'Creating embeddings and vector base'
        )

        GenerateEmbeddings.create_vector_base(download_dir)

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.SUCCESS,
            result = 'Creating FAISS vector base success'
        )


    except ValidationError as e:
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = str(e)
        )

        raise e

    except IntegrityError:
        LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = str(e)
        )

    except Exception as e:
        LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())
        
        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = str(e)
        )

        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)



def get_response_from_vector_base():
    ''''''