import os
import re
import gc
import json
import requests
from io import BytesIO

import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from decouple import config
from bs4 import BeautifulSoup
import torch

from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

from .models import Document, Chat, Message


class FetchDataService:
    ''''''

    def __init__(self, train_data_url: str, test_data_url: str) -> object:
        self._train_data_url = train_data_url
        self._test_data_url = test_data_url

    def _get_url_data_from_huggingface(self, url: str) -> list[str]:
        ''''''

        response = requests.get(url)
        response.raise_for_status()

        return response.json()
    
    def fetch_data(self) -> pd.DataFrame:
        ''''''

        urls = self._get_url_data_from_huggingface(self._train_data_url)
        test_urls = self._get_url_data_from_huggingface(self._test_data_url)

        urls.extend(test_urls)

        dfs = []

        for url in urls:
            response = requests.get(url)
            response.raise_for_status()
            
            parquet_file = BytesIO(response.content)
            
            df = pd.read_parquet(parquet_file)
            dfs.append(df)

        full_df = pd.concat(dfs, ignore_index = True)

        full_df['metadata'] = full_df['metadata'].str[0]

        return full_df



class DataConsolidationService:
    ''''''

    def __init__(self, full_df: pd.DataFrame) -> object:
        self._full_df = full_df

    def _join_texts(self, series):
        ''''''

        return "\n\n---\n\n".join(series.dropna().astype(str).unique())

    def _group_question_answer(self) -> pd.DataFrame:
        ''''''

        consolidated_df = self._full_df.groupby('qid').agg(
            question = ('question', 'first'),
            metadata = ('metadata', 'first'),
            response_j = ('response_j', self._join_texts),
            response_k = ('response_k', self._join_texts)
        ).reset_index()

        consolidated_df['consolidated_answers'] = consolidated_df['response_j'] + "\n\n---\n\n" + consolidated_df['response_k']
        consolidated_df.drop(columns = ['response_j', 'response_k'], inplace = True)

        return consolidated_df

    def _classify_relevant_sentences(self, consolidated_df: pd.DataFrame) -> pd.DataFrame:
        ''''''

        consolidated_df_processed = consolidated_df.copy()

        consolidated_df_processed['full_text_lower'] = (
            consolidated_df_processed['question'].str.lower() + " " + consolidated_df_processed['consolidated_answers'].str.lower()
        )

        python_keywords_regex = r'python|pandas|numpy|django|flask|\bdef\b|\bclass\b|\bimport\b|\bself\b'
        other_lang_keywords_regex = r'php|objective-c|java|c\#|swift|javascript'

        consolidated_df_processed['python_signal_count'] = consolidated_df_processed['full_text_lower'].str.findall(python_keywords_regex, flags = re.IGNORECASE).str.len()

        consolidated_df_processed['is_other_lang'] = consolidated_df_processed['full_text_lower'].str.contains(other_lang_keywords_regex, na = False, case = False)
        consolidated_df_processed['has_code_block'] = consolidated_df_processed['consolidated_answers'].str.contains('```', na = False)

        return consolidated_df_processed
    
    def _filter_by_flags(self, consolidated_df: pd.DataFrame) -> pd.DataFrame:
        ''''''

        final_mask = (
            (consolidated_df['python_signal_count'] >= 3) & 
            (~consolidated_df['is_other_lang']) & 
            (consolidated_df['has_code_block'])
        )

        focused_df = consolidated_df[final_mask].copy()

        focused_df.drop(columns = ['full_text_lower', 'python_signal_count', 'is_other_lang', 'has_code_block'], inplace = True)

        return focused_df

    def consolidate_data(self) -> None:
        ''''''

        consolidated_df = self._group_question_answer()

        consolidated_df_processed = self._classify_relevant_sentences(consolidated_df)

        focused_df = self._filter_by_flags(consolidated_df_processed)

        focused_df.reset_index(inplace = True)
        focused_df = focused_df.rename(columns = {'index': 'parent_index'})

        #focused_df.to_pickle("focused_database.pkl")

        documents = [
            Document(
                parent_index = row['parent_index'],
                qid = row['qid'],
                question = row['question'],
                metadata = row['metadata'],
                consolidated_answers = row['consolidated_answers']
            )
            for row in focused_df.to_dict(orient = 'records')
        ]

        Document.objects.bulk_create(documents)



class CreateFaissTreeService:
    ''''''

    def __init__(self) -> object:
        queryset = Document.objects.values()

        self._focused_df = pd.DataFrame.from_records(queryset)

    def _clean_text(self, text: str) -> str:
        ''''''
        
        if not isinstance(text, str):
            return ""
        
        try:
            soup = BeautifulSoup(text, "lxml")
            
            text = soup.get_text()
        
        except Exception:
            pass
        
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags = re.MULTILINE)
        text = re.sub(r'\[([^\]]*)\]\([^\)]*\)?', r'\1', text)
        text = re.sub(r'```[a-zA-Z]*\n', '', text)
        text = text.replace('```', '')
        text = text.replace('`', '')
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def _create_chunks(self) -> pd.DataFrame:
        ''''''

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 2000,
            chunk_overlap = 400,
            separators = ["\n\n", "\n", " ", ""],
            length_function = len
        )

        focused_df_processed = self._focused_df.copy()

        focused_df_processed['text_for_chunking'] = focused_df_processed['question'] + "\n\nAnswers:\n" + focused_df_processed['consolidated_answers']

        focused_df_processed['raw_chunks'] = focused_df_processed['text_for_chunking'].apply(lambda text: text_splitter.split_text(text))

        documents_df = focused_df_processed[['parent_index', 'metadata', 'raw_chunks']].explode('raw_chunks')
        documents_df = documents_df.rename(columns = {'raw_chunks': 'raw_text_chunk'})

        documents_df['cleaned_text_chunk'] = documents_df['raw_text_chunk'].apply(self._clean_text)

        documents_df = documents_df[documents_df['cleaned_text_chunk'].str.strip().astype(bool)].reset_index(drop = True)

        return documents_df
    
    def create_faiss_index(self, batch_size = 1024, faiss_save_path = 'faiss_index') -> None:
        ''''''

        documents_df = self._create_chunks()

        vectorstore = None
        total_docs = len(documents_df)

        embedding_model = HuggingFaceEmbeddings(
            model_name = 'all-MiniLM-L6-v2',
            model_kwargs = {"device": "cuda" if torch.cuda.is_available() else "cpu"}
        )

        for i in tqdm(range(0, total_docs, batch_size), desc = "Processando lotes"):
            batch_df = documents_df.iloc[i:i + batch_size]
            
            texts_to_embed = batch_df['cleaned_text_chunk'].tolist()
            
            texts_to_store = batch_df['raw_text_chunk'].tolist()
            
            metadatas = [
                {'parent_index': row.parent_index, 'metadata_link': row.metadata} 
                for row in batch_df.itertuples(index = False)
            ]

            if not texts_to_embed:
                continue
            
            embeddings = embedding_model.embed_documents(texts_to_embed)

            text_embedding_pairs = list(zip(texts_to_store, embeddings))
            
            if vectorstore is None:
                vectorstore = FAISS.from_embeddings(text_embedding_pairs, embedding_model, metadatas=metadatas)
            
            else:
                vectorstore.add_embeddings(text_embedding_pairs, metadatas=metadatas)
            
            gc.collect()

        if vectorstore:
            vectorstore.save_local(faiss_save_path)
        
        else:
            raise ValueError("O vectorstore não foi criado. Nenhum documento foi processado ou adicionado ao índice.")



class GetResponseFromGeminiService:
    ''''''

    def __init__(self, faiss_path: str, model_name: str = "gemini-1.5-flash") -> object:
        os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")
        
        self.embedding_model = HuggingFaceEmbeddings(
            model_name = 'all-MiniLM-L6-v2',
            model_kwargs = {'device': 'cpu'}
        )
        
        self.llm = ChatGoogleGenerativeAI(model = model_name, temperature = 0.3)
        
        self.vectorstore = FAISS.load_local(
            faiss_path, 
            embeddings = self.embedding_model, 
            allow_dangerous_deserialization = True
        )

    def classify_greeting(self, question: str) -> str:
        ''''''
        
        prompt_template = """
            Você é um classificador de saudações. Seu trabalho é verificar se uma frase enviada por um usuário é uma saudação como "olá", "oi", "bom dia", etc.
            - Se for uma saudação, responda com uma saudação apropriada, como "Olá!", "Boa noite!", etc.
            - Se não for uma saudação, responda apenas com a palavra: other
            Frase: {question}
            Resposta:
        """

        greeting_llm = ChatGoogleGenerativeAI(model = "gemini-1.5-flash", temperature=0.7)
        
        chain = PromptTemplate.from_template(prompt_template) | greeting_llm
        answer = chain.invoke({"question": question})
        
        result = answer.content.strip().lower()
        
        return result if result != "other" else "other"
    
    def _choose_best_prompt(self, best_score: float) -> str:
        ''''''

        HIGH_CONFIDENCE_THRESHOLD = 0.85
        MEDIUM_CONFIDENCE_THRESHOLD = 1.1

        if best_score < HIGH_CONFIDENCE_THRESHOLD:
            return """
                Você é um assistente de programação especialista em Python, preciso e direto. Baseado estritamente no contexto a seguir, responda à pergunta do usuário. Se a resposta contiver código, formate-o corretamente.

                Contexto:
                {context}

                Pergunta do Usuário:
                {question}
            """
        
        elif best_score < MEDIUM_CONFIDENCE_THRESHOLD:
            return """
                Você é um assistente de programação especialista e um excelente professor. O contexto fornecido abaixo é tematicamente relacionado à pergunta do usuário, mas pode não ser uma resposta direta. Sua principal tarefa é analisar esses exemplos práticos e sintetizar o princípio geral que eles demonstram. Comece sua resposta de forma cautelosa (ex: "Com base nas informações disponíveis...").

                Contexto:
                {context}

                Pergunta do Usuário:
                {question}
            """
        
        else:
            return json.dumps([{"response": "Não encontrei informações suficientemente relevantes.", "references": []}], indent = 2)
        
    def _filter_best_references(self, vector_results) -> list:
        ''''''

        L2_DISTANCE_THRESHOLD = 1.0

        filtered_results = []
        
        if vector_results:
            filtered_results.append(vector_results[0])
            
            for doc, score in vector_results[1:]:
                if score <= L2_DISTANCE_THRESHOLD:
                    filtered_results.append((doc, score))

        return filtered_results

    def _retrieve_original_ref_index(self, filtered_results: list) -> dict:
        ''''''

        parent_indices = {}
        
        for doc, score in filtered_results:
            parent_index = doc.metadata.get('parent_index')
            
            if parent_index is not None:
                if parent_index not in parent_indices or score < parent_indices[parent_index]['similarity']:
                    parent_indices[parent_index] = {'similarity': score}

        return parent_indices
    
    def _create_response(self, parent_indices: dict, response_text) -> list:
        ''''''

        references_list = []
        
        for index, data in parent_indices.items():
            original_doc_row = Document.objects.filter(parent_index = index).values().first()

            if original_doc_row:
                l2_distance = data['similarity']
                
                references_list.append({
                    "content": original_doc_row['consolidated_answers'],
                    "similarity_percentage": f"{np.exp(-l2_distance):.2%}", 
                    "metadata": original_doc_row['metadata']
                })

        return [{"response": response_text, "references": references_list}]



    def get_answer(self, question: str, top_k: int = 5) -> str:
        ''''''

        vector_results = self.vectorstore.similarity_search_with_score(query = question, k = top_k)

        if not vector_results:
            return json.dumps([{"response": "Desculpe, não encontrei nenhuma informação.", "references": []}], indent = 2)

        best_score = vector_results[0][1]
        context_for_llm = "\n\n---\n\n".join([doc.page_content for doc, score in vector_results])

        appropriate_prompt = self._choose_best_prompt(best_score)

        prompt_template = PromptTemplate.from_template(appropriate_prompt)
        chain = prompt_template | self.llm
        
        gemini_answer = chain.invoke({"context": context_for_llm, "question": question})
        response_text = gemini_answer.content

        filtered_results = self._filter_best_references(vector_results)
        parent_indices = self._retrieve_original_ref_index(filtered_results)
        final_output = self._create_response(parent_indices, response_text)
        
        return json.dumps(final_output, indent = 2)



class ChatService:
    ''''''
    
    @staticmethod
    def create(request: Request) -> dict:
        ''''''

        chat_name = request.data.get('chat_name')
            
        if not chat_name:
            raise ValidationError("error: chat_name field is required.")

        user = request.user
        chat = Chat.objects.create(user = user, name = chat_name)

        chat = {
            "message": "Chat created succesfully",
            "chat_id": chat.id,
            "name": chat.name,
            "created_at": chat.created_at
        }

        return chat
    
    @staticmethod
    def list_chats(request: Request) -> list:
        ''''''

        chats = Chat.objects.filter(user = request.user)
            
        chat_data = []
        
        for chat in chats:
            chat_data.append({
                'id': chat.id,
                'chat_name': chat.name,
                'user_id': chat.user.id,
                'created_at': chat.created_at,
            })

        return chat_data
    
    @staticmethod
    def delete(request: Request, pk: int) -> str:
        ''''''

        chat = get_object_or_404(Chat, id = pk, user = request.user)
            
        chat_name = chat.name

        chat.delete()

        return chat_name


class MessageService:
    ''''''
    
    @staticmethod
    def create(request: Request, chat_id: int) -> dict:
        ''''''
        
        text = request.data.get('text')
        is_user = request.data.get('is_user')

        if text is None or is_user is None:
            raise ValidationError("error: text and is_user fields are required.")

        if isinstance(text, dict):
            text = json.dumps(text)
        
        elif isinstance(text, str):
            try:
                parsed = json.loads(text)
                
                text = json.dumps(parsed)
            
            except json.JSONDecodeError:
                # Não é JSON válido, deixa como string normal
                pass

        chat = get_object_or_404(Chat, id=chat_id, user=request.user)

        message = Message.objects.create(
            chat = chat,
            is_user = is_user,
            text = text
        )

        return {
            'id': message.id,
            'chat_id': chat.id,
            'is_user': message.is_user,
            'text': message.text,
            'created_at': message.created_at
        }
    
    @staticmethod
    def list_messages(chat_id: int) -> list:
        ''''''
        
        messages = Message.objects.filter(chat_id=chat_id)
        messages_data = []

        for message in messages:
            try:
                text = json.loads(message.text)
            
            except (json.JSONDecodeError, TypeError):
                text = message.text

            messages_data.append({
                'id': message.id,
                'text': text,
                'is_user': message.is_user,
                'created_at': message.created_at,
                'chat_id': message.chat_id,
            })

        return messages_data