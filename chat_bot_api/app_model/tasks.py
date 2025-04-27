import os
import traceback
import shutil

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from celery import shared_task, states

from .models import TaskStatus
from .services import PrepareDataService, SetDocumentsOnDatabase, GenerateEmbeddings, GetResponseFromGemini
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



def get_response_from_vector_base(question: str, data_base_path: str) -> str:
    ''''''

    LIMIAR_REJEICAO = 1.0833

    if not question:
        raise ValidationError('no sentence provided for search.')
    
    
    verify_greetings = GetResponseFromGemini.classify_greeting_with_gemini(question)

    if verify_greetings != 'other':
        return verify_greetings
    
    
    vector_results, gemini_answer = GetResponseFromGemini.get_answer_from_model(question, data_base_path)

    if not vector_results or vector_results[0][1] > LIMIAR_REJEICAO:
        return "Sorry, I couldn't find anything related to your question. This content may not be in my search database. Could you rephrase it?"


    formatted_results = [
        {
            "result_number": i,
            "content": doc.page_content,
            "similarity": round(1 / (1 + score), 4)
        }
        for i, (doc, score) in enumerate(vector_results, 1)
    ]

    response_string = ""

    response_string += "\n🤖 Gemini: "
    response_string += gemini_answer.content
    response_string += "--------------------------------------"
    response_string += "🤖 I used these results as a reference:"

    for i, result in enumerate(formatted_results, 1):
        response_string += f"\n\n🔹 {i}) {result['content']}\n"
        response_string += f"\n📎 Similarity: {result['similarity']:.4f}\n"

    return response_string
