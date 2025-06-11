import os
import gc
import traceback
import shutil
import requests

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from celery import shared_task, states

from .models import TaskStatus, Document
from .services import FetchDataService, DataConsolidationService, CreateFaissTreeService, GetResponseFromGeminiService
from core.models import LogSystem


@shared_task
def set_database_and_train_data(faiss_save_dir: str):
    task_id = set_database_and_train_data.request.id
    
    try:
        TaskStatus.objects.get_or_create(
            task_id = task_id,
            defaults = {'status': states.PENDING, 'result': 'Iniciando processamento'}
        )

        Document.objects.all().delete()
        
        fetch_data = FetchDataService(
            "https://huggingface.co/api/datasets/tyson0420/stackexchange-overflow-fil-python/parquet/default/train",
            "https://huggingface.co/api/datasets/tyson0420/stackexchange-overflow-fil-python/parquet/default/test"
        )

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.PENDING,
            result = 'Analisando dados e criando lotes de QIDs'
        )
        
        qid_batches = fetch_data.get_qid_batches()
        total_batches = len(qid_batches)
        total_documents_saved = 0

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.PENDING,
            result = f'Processando {total_batches} lotes de dados'
        )

        for batch_idx, qid_batch in enumerate(qid_batches, 1):
            TaskStatus.objects.filter(task_id = task_id).update(
                status = states.PENDING,
                result = f'Processando lote {batch_idx}/{total_batches} - Baixando dados'
            )
            
            batch_df = fetch_data.fetch_data_by_qids(qid_batch)
            
            TaskStatus.objects.filter(task_id = task_id).update(
                status = states.PENDING,
                result = f'Processando lote {batch_idx}/{total_batches} - Consolidando dados'
            )
            
            data_consolidation = DataConsolidationService(batch_df)
            docs_saved = data_consolidation.consolidate_batch()
            total_documents_saved += docs_saved
            
            del batch_df, data_consolidation
            gc.collect()
            
            TaskStatus.objects.filter(task_id = task_id).update(
                status = states.PENDING,
                result = f'Lote {batch_idx}/{total_batches} concluído - {docs_saved} documentos salvos'
            )

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.PENDING,
            result = f'Dados consolidados: {total_documents_saved} documentos. Criando embeddings e índice FAISS'
        )

        create_faiss_index = CreateFaissTreeService()
        create_faiss_index.create_faiss_index(
            batch_size = 512,
            faiss_save_path = faiss_save_dir,
            task_id = task_id
        )

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.SUCCESS,
            result = f'Processamento concluído! {total_documents_saved} documentos processados e índice FAISS criado'
        )

        fetch_data.clear_cache()
        gc.collect()

    except requests.HTTPError as e:
        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = f'Erro ao baixar dados: {str(e)}'
        )

    except ValidationError as e:
        if os.path.exists(faiss_save_dir):
            shutil.rmtree(faiss_save_dir)

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = f'Erro de validação: {str(e)}'
        )

    except IntegrityError as e:
        LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())

        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = f'Erro de integridade no banco: {str(e)}'
        )

    except Exception as e:
        LogSystem.objects.create(error = str(e), stacktrace = traceback.format_exc())
        
        TaskStatus.objects.filter(task_id = task_id).update(
            status = states.FAILURE,
            result = f'Erro inesperado: {str(e)}'
        )

        if os.path.exists(faiss_save_dir):
            shutil.rmtree(faiss_save_dir)



def get_response_from_vector_base(question: str, faiss_path: str) -> str:
    ''''''

    if not question:
        raise ValidationError('no sentence provided for search.')
    
    get_reponse_from_gemini = GetResponseFromGeminiService(faiss_path = faiss_path)

    verify_greetings = get_reponse_from_gemini.classify_greeting(question)

    if verify_greetings != 'other':
        return verify_greetings
    
    response = get_reponse_from_gemini.get_answer(question)

    return response
    
