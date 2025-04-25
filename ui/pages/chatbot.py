import time
import requests
from pathlib import Path
import streamlit as st
from streamlit_autorefresh import st_autorefresh


def get_profile_image(role):
    if role == "user":
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    
    else:
        return "https://cdn-icons-png.flaticon.com/512/4712/4712109.png"

def update_chat():
    with message_container.container():
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            profile_img = get_profile_image(role)

            if content.startswith("<div"): 
                st.markdown(content, unsafe_allow_html = True)
            
            else:
                if role == "user":
                    st.markdown(f'''
                        <div class="message-container" style="justify-content: flex-end;">
                            <div class="message user">
                                <div class="message-content">{content}</div>
                            </div>
                            <img class="profile-img" src="{profile_img}" alt="{role}">
                        </div>
                    ''', unsafe_allow_html = True)
                
                else:
                    st.markdown(f'''
                        <div class="message-container" style="justify-content: flex-start;">
                            <img class="profile-img" src="{profile_img}" alt="{role}">
                            <div class="message bot">
                                <div class="message-content">{content}</div>
                            </div>
                        </div>
                    ''', unsafe_allow_html = True)



def check_pipeline_ready():
    project_root = Path(__file__).resolve().parent.parent.parent
    base_path = project_root / "data"
    
    required_files = [
        base_path / "processed/faiss_index/index.pkl",
        base_path / "processed/faiss_index/index.faiss",
        base_path / "raw/stackexchange_full.parquet",
    ]

    #for f in required_files:
    #    st.write(f"Verificando: {f} - Existe? {f.exists()}")
    
    return all(f.exists() for f in required_files)


def start_pipeline():
    try:
        token = st.session_state.get("access_token", None)
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        response = requests.post("http://localhost:8000/app_model/train/model/", headers = headers)
        
        if response.status_code == 201:
            task_id = response.json().get("task_id")
            
            if task_id:
                st.session_state["task_id"] = task_id
                
                return True
        
        return False

    except Exception:
        return False


def check_pipeline_status():
    try:
        task_id = st.session_state.get("task_id", None)
        
        if not task_id:
            return {"status": "ERROR", "result": "Task ID não encontrado"}

        token = st.session_state.get("access_token", None)
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        data = {"task_id": task_id}

        response = requests.post("http://localhost:8000/app_model/monitor/training/", json = data, headers = headers)

        if response.status_code == 200:
            return response.json()

        return {"status": "ERROR", "result": "Erro ao consultar status"}
    
    except Exception as e:
        return {"status": "ERROR", "result": f"Erro ao conectar ao servidor: {str(e)}"}



def query_model(prompt):
    payload = {
        "prompt": prompt
    }

    token = st.session_state.get("access_token", None)

    if not token:
        st.error("Token de autenticação não encontrado. Faça login novamente.")
        
        return "⚠️ Erro de autenticação. Por favor, faça login novamente."

    headers = {
        "Authorization": f"Bearer {token}"
    }

    API_MODEL_URL = "http://localhost:8000/app_model/search/information/"

    try:
        response = requests.post(API_MODEL_URL, json = payload, headers = headers)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code in [401, 403]:
            st.warning("🔒 Sua sessão expirou. Por favor, faça login novamente.")

            if st.button("🔑 Ir para Login"):
                st.switch_page("pages/login.py")
            
            return "🔒 Sua sessão expirou. Por favor, faça login novamente."
        
        else:
            st.error(f"Erro {response.status_code} ao consultar o modelo.")
            
            return "Desculpe, não consegui entender sua pergunta."
    
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")
        
        return "Desculpe, não consegui conectar ao servidor."

    
###################################################################################################################


st.title("💬 Chatbot for Stack Exchange")
st.subheader("Inferences in Stack Exchange (SE) question-answering dataset")

st.markdown("""
    <style>
    .message {
        padding: 10px 15px;
        border-radius: 15px;
        margin: 8px 0;
        max-width: 70%;
        font-size: 16px;
        line-height: 1.4;
        display: flex;
        align-items: center;  /* Alinha as mensagens verticalmente */
    }
    .user {
        background-color: #9B4DFF;
        color: white;
        float: right;
        text-align: right;
        justify-content: flex-end;
    }
    .bot {
        background-color: #4f4f4f;
        float: left;
        text-align: left;
    }
    .profile-img {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin: 0 15px;
    }
    .user .message-content {
        margin-left: 10px;
    }
    .bot .message-content {
        margin-right: 10px;
    }
    .message-container {
        display: flex;
        align-items: center;  /* Alinha a imagem ao meio em relação à mensagem */
        margin-bottom: 10px;
    }

    /* Animação typing */
    .thinking-message-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin: 5px 0;
    }

    .thinking-bubble {
        background-color: #4f4f4f;
        border-radius: 15px;
        padding: 1px 4px;
        font-size: 15px;
        line-height: 1;
        display: inline-block;
        /* color: #333; */
        white-space: nowrap;
    }

    .typing span {
        animation: blink 1.5s infinite;
    }

    .typing span:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing span:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes blink {
        0% { opacity: 0.2; }
        20% { opacity: 1; }
        100% { opacity: 0.2; }
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    </style>
""", unsafe_allow_html = True)


if "messages" not in st.session_state:
    st.session_state.messages = []


if st.button("🧹 Limpar conversa"):
    st.session_state.messages = []



if "pipeline_ready" not in st.session_state:
    st.session_state.pipeline_ready = check_pipeline_ready()

if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False

if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = "Aguardando início..."

if "last_status_check" not in st.session_state:
    st.session_state.last_status_check = 0


message_container = st.empty()



if not st.session_state.get("pipeline_ready", False):
    
    if not st.session_state.get("pipeline_running", False):
        if st.button("🚀 Iniciar preparação dos dados"):
            success = start_pipeline()
            
            if success:
                st.session_state.pipeline_running = True
                st.session_state.pipeline_status = "Pipeline iniciado."
                st.session_state.last_status_check = time.time()
            
            else:
                st.error("Erro ao iniciar o pipeline.")
    else:
        now = time.time()
        
        if now - st.session_state.last_status_check > 15:
            status_json = check_pipeline_status()
            
            if isinstance(status_json, str):
                st.session_state.pipeline_status = status_json
            
            else:
                result = status_json.get("result", "").lower()
                status = status_json.get("status", "").upper()

                st.session_state.pipeline_status = result
                st.session_state.last_status_check = now

                if status == "SUCCESS" and "faiss vector base success" in result:
                    st.session_state.pipeline_ready = True
                    st.session_state.pipeline_running = False

    if not st.session_state.pipeline_ready:
        st.info(f"⏳ Status atual: {st.session_state.pipeline_status}")
        st_autorefresh(interval = 15000, limit = None, key = "pipeline_refresh")
        st.stop()



user_input = st.chat_input("Digite sua mensagem")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    update_chat()

    thinking_html = '''
    <div class="thinking-message-container">
        <div class="thinking-bubble">
            <span class="typing">thinking <span>.</span><span>.</span><span>.</span></span>
        </div>
    </div>
    '''

    st.session_state.messages.append({"role": "bot", "content": thinking_html})
    update_chat()

    model_response = query_model(user_input)
    st.session_state.messages[-1] = {"role": "bot", "content": model_response}
    update_chat()
