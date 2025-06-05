import os
import re
import json
import shutil
import pandas as pd
from decouple import config
from bs4 import BeautifulSoup

from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

import torch
from datasets import load_dataset
from langchain.docstore.document import Document as LangChainDocument
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

from .models import Document, Chat, Message



class PrepareDataService:
    ''''''
    
    def __init__(self):
        # for non static methods
        pass

    def _clean_html(self, raw_html: str) -> str:
        ''''''

        return BeautifulSoup(raw_html, "html.parser").get_text(separator = " ").strip()

    def _clean_whitespace(self, text: str) -> str:
        ''''''

        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def _clean_and_format_data(self, df: pd.DataFrame) -> pd.DataFrame:
        ''''''
        
        df['clean_title'] = df['title'].apply(lambda x: self._clean_html(str(x)))
        df['clean_body'] = df['body'].apply(lambda x: self._clean_html(str(x)))

        df['clean_text'] = df['clean_title'] + ". " + df['clean_body']

        df['clean_text'] = df['clean_text'].apply(self._clean_whitespace)

        return df

    @staticmethod
    def get_huggingface_data_and_save(download_dir_path: str) -> None:
        ''''''

        dataset_folder_path = os.path.join(download_dir_path, "raw")
        dataset_file_path = os.path.join(dataset_folder_path, "stackexchange_full.parquet")
        
        if os.path.exists(dataset_folder_path):
            shutil.rmtree(dataset_folder_path)
        
        dataset = load_dataset("habedi/stack-exchange-dataset", split = 'train')
        df = dataset.to_pandas()

        prepare_data_service = PrepareDataService()
        df = prepare_data_service._clean_and_format_data(df)

        os.makedirs(dataset_folder_path, exist_ok = True)

        df.to_parquet(dataset_file_path, index = False)



class SetDocumentsOnDatabaseService:
    ''''''

    @staticmethod
    def set_data_on_postgre(download_dir_path: str) -> None:
        ''''''
        
        Document.objects.all().delete()

        dataset_file_path = os.path.join(download_dir_path, "raw", "stackexchange_full.parquet")

        df = pd.read_parquet(dataset_file_path)

        documents = [
            Document(
                title = row['clean_title'],
                body = row['clean_body'],
                text = row['clean_text'],
                tags = row['tags'],
                label = row['label']
            )
            for row in df.to_dict(orient = 'records')
        ]

        Document.objects.bulk_create(documents)
        



class GenerateEmbeddingsService:
    ''''''
    
    def __init__(self):
        # for non static methods
        pass

    def _create_documents(self) -> list[LangChainDocument]:
        ''''''

        queryset = Document.objects.values("id", "text")

        
        documents = [
            LangChainDocument(page_content = item["text"], metadata = {"postgres_id": item["id"]}) 
            for item in queryset
        ]

        return documents
    
    @staticmethod
    def define_embedding_model() -> HuggingFaceEmbeddings:
        ''''''
        
        embedding_model = HuggingFaceEmbeddings(
            model_name = "sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs = {"device": "cuda" if torch.cuda.is_available() else "cpu"},
            encode_kwargs = {"batch_size": 64}
        )

        return embedding_model
    
    def _create_faiss_index(self, documents: list[LangChainDocument], embedding_model: HuggingFaceEmbeddings):
        '''
        Euclidian Distante L2
        '''
        
        vectorstore = FAISS.from_documents(documents, embedding_model)
        
        return vectorstore

    
    @staticmethod
    def create_vector_base(vector_base_local_path: str) -> None:
        ''''''

        vector_save_path = os.path.join(vector_base_local_path, "processed", "faiss_index")

        generate_embeddings = GenerateEmbeddingsService()

        documents = generate_embeddings._create_documents()
        embedding_model = GenerateEmbeddingsService.define_embedding_model()
        faiss_index = generate_embeddings._create_faiss_index(documents, embedding_model)

        faiss_index.save_local(vector_save_path)



class GetResponseFromGeminiService:
    ''''''
    
    def __init__(self):
        # for non static methods
        pass

    def _define_gemini_model(self, model = "gemini-1.5-flash", temperature = 0.3, prompt_template = ""):
        ''''''
        
        os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")

        llm = ChatGoogleGenerativeAI(model = model, temperature = temperature)

        gemini_prompt = PromptTemplate.from_template(
            prompt_template
        )

        chain = gemini_prompt | llm

        return chain
    
    def _search_vector_base(self, vectorstore_path: str, query: str, top_k: int):
        ''''''

        embedding_model = GenerateEmbeddingsService.define_embedding_model()

        vectorstore = FAISS.load_local(
            vectorstore_path, 
            embeddings = embedding_model, 
            allow_dangerous_deserialization = True
        )
        
        vector_results = vectorstore.similarity_search_with_score(query, k = top_k)

        context = "\n\n".join([doc.page_content for doc, _ in vector_results])

        return context, vector_results
    

    @staticmethod
    def classify_greeting_with_gemini(question: str) -> str:
        ''''''

        prompt_template = """
            You are a greeting classifier.
            Your job is to check if a sentence sent by a user is a greeting like "hello", "hi", "good morning", "good afternoon", "good evening", etc.

            - If it is a greeting, respond with an appropriate greeting back, like "Hello!", "Good evening!", etc.
            - If it is not a greeting, respond with just: other

            Sentence: {question}
            Answer:
        """

        get_response_from_gemini = GetResponseFromGeminiService()

        chain = get_response_from_gemini._define_gemini_model(
            prompt_template = prompt_template, 
            temperature = 0.7
        )

        answer = chain.invoke({"question": question})

        result = answer.content.strip().lower()
        
        if result != "other":
            return result
        else:
            return "other"



    @staticmethod
    def get_answer_from_model(question: str, data_base_path: str):
        ''''''

        # How are threads implemented in different OSs?
        # What is complement of Context-free languages?

        prompt_template = """
            You are a helpful assistant. 
            Based on the following content retrieved from the database:\n\n{context}\n\n
            Answer the user's question clearly and naturally:\n\n
            Question: {question}
        """

        faiss_path = os.path.join(data_base_path, "processed", "faiss_index")

        get_response_from_gemini = GetResponseFromGeminiService()

        chain = get_response_from_gemini._define_gemini_model(prompt_template = prompt_template)

        context, vector_results = get_response_from_gemini._search_vector_base(faiss_path, question, 3)

        gemini_answer = chain.invoke({"context": context, "question": question})

        return vector_results, gemini_answer
    


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