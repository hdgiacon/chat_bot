import streamlit as st
import requests

API_LOGIN_URL = "http://localhost:8000/app_auth/login/"  # altere se necessário


# Ocultar barra lateral de navegação
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"  # Fecha a sidebar por padrão
)

# CSS para esconder completamente a barra lateral
hide_sidebar_style = """
    <style>
        section[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)


# Inicializa a página
if "page" not in st.session_state:
    st.session_state.page = "login"

def go_to_register():
    st.session_state.page = "register"

def go_to_login():
    st.session_state.page = "login"

def login(username, password):
    payload = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(API_LOGIN_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            
            # Salva os tokens na sessão
            st.session_state.access_token = data["access"]
            st.session_state.refresh_token = data["refresh"]
            
            # Redireciona para o chatbot (lembre que o nome do arquivo deve ser igual ao mostrado no Streamlit)
            st.switch_page("pages/chatbot.py") # se estiver na pasta 'pages'

        else:
            st.error("Usuário ou senha incorretos.")
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")

# Estilo CSS
st.markdown("""
    <style>
        .login-box {
            max-width: 400px;
            margin: auto;
            padding: 2rem;
            background-color: #f1f1f1;
            border-radius: 10px;
        }
        .login-box h2 {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .switch-link {
            text-align: center;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

# Interface
with st.container():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    if st.session_state.page == "login":
        st.markdown("## 🔐 Login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            login(username, password)
        st.button("Cadastrar", on_click=go_to_register, use_container_width=True)

    elif st.session_state.page == "register":
        st.markdown("## 📝 Cadastrar")
        new_username = st.text_input("Novo usuário")
        new_password = st.text_input("Nova senha", type="password")
        st.button("Cadastrar", use_container_width=True)
        st.button("Voltar para Login", on_click=go_to_login, use_container_width=True)

    elif st.session_state.page == "chat":
        st.markdown("## 🤖 Bem-vindo ao Chatbot!")
        st.success("Login realizado com sucesso.")
        st.write("Você está autenticado. Aqui entrará a interface do chatbot.")
        st.button("Sair", on_click=lambda: st.session_state.clear(), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
