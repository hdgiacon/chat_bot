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



def get_response_from_vector_base(question: str, data_base_path: str):
    ''''''

    if not question:
        raise ValidationError('no sentence provided for search.')
    
    # TODO: modelo gemini que vai analisar se a mensagem do usuário é uma duvida a se consultar no banco ou se é tipo uma mensagem de bom dia

    # se for algo como uma mensagem de bom dia, não se deve consultar no banco

    #first_analisys = GetResponseFromGemini.gemini_pre_analisys(question)

    #if first_analisys == 'consult_vector_base':
    vector_results, gemini_answer = GetResponseFromGemini.get_answer_from_model(question, data_base_path)

    formatted_results = [
        {
            "numero_resultado": i,
            "conteudo": doc.page_content,
            "similaridade": round(1 / (1 + score), 4)
        }
        for i, (doc, score) in enumerate(vector_results, 1)
    ]

    response_string = ""

    response_string += "\n🤖 Gemini: "
    response_string += gemini_answer.content + "\n\n"
    response_string += "Utilizei esses resultados como referência:"

    for i, result in enumerate(formatted_results, 1):
        response_string += f"\n\n🔹 {i}) {result['conteudo']}\n"
        response_string += f"\n📎 Similaridade: {result['similaridade']:.4f}\n"

    return response_string
