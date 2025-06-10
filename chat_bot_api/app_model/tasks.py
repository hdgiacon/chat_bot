import os
import traceback
import shutil
import requests

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from celery import shared_task, states

from .models import TaskStatus
from .services import FetchDataService, DataConsolidationService, CreateFaissTreeService, GetResponseFromGeminiService
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

        fetch_data = FetchDataService(
            "https://huggingface.co/api/datasets/tyson0420/stackexchange-overflow-fil-python/parquet/default/train",
            "https://huggingface.co/api/datasets/tyson0420/stackexchange-overflow-fil-python/parquet/default/test"
        )

        full_df = fetch_data.fetch_data()

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.PENDING,
            result = 'Setting data on Postgre database'
        )

        data_consolidation = DataConsolidationService(full_df)

        data_consolidation.consolidate_data()

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.PENDING,
            result = 'Creating embeddings and vector base'
        )

        create_faiss_index = CreateFaissTreeService('focused_database.pkl')

        create_faiss_index.create_faiss_index()

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.SUCCESS,
            result = 'Creating FAISS vector base success'
        )

    except requests.HTTPError:
        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = str(e)
        )


    except ValidationError as e:
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = str(e)
        )

    except IntegrityError as e:
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



def get_response_from_vector_base(question: str) -> str:
    ''''''

    if not question:
        raise ValidationError('no sentence provided for search.')
    
    get_reponse_from_gemini = GetResponseFromGeminiService('faiss_index', 'focused_database.pkl')

    verify_greetings = get_reponse_from_gemini.classify_greeting(question)

    if verify_greetings != 'other':
        return verify_greetings
    
    response = get_reponse_from_gemini.get_answer(question)

    return response
    
