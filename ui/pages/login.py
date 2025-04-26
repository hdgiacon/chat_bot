import streamlit as st
import requests


API_LOGIN_URL = "http://localhost:8000/app_auth/login/"
API_CREATE_USER_URL = "http://localhost:8000/user/create/"

st.set_page_config(
    page_title = "Login",
    page_icon = "🔐",
    layout = "centered",
    initial_sidebar_state = "collapsed"
)

hide_sidebar_style = """
    <style>
        section[data-testid="stSidebarNav"] {display: none;}
    </style>
"""

st.markdown(hide_sidebar_style, unsafe_allow_html = True)


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
        response = requests.post(API_LOGIN_URL, json = payload)
        
        if response.status_code == 200:
            data = response.json()
            
            st.session_state.access_token = data["access"]
            st.session_state.refresh_token = data["refresh"]
            
            st.switch_page("pages/chatbot.py")

        else:
            st.error("Incorrect username or password.")
    
    except Exception as e:
        st.error(f"Error connecting to API: {e}")

def register(new_username, new_password):
    payload = {
        "username": new_username,
        "password": new_password,
        "email": "test@test.com",
        "is_staff": True
    }

    try:
        response = requests.post(API_CREATE_USER_URL, json = payload)

        if response.status_code == 201:
            st.session_state.page = "login"
            st.success("User created successfully.")
            st.rerun()

        else:
            st.error("New password not allowed.")

    except Exception as e:
        st.error(f"Error connecting to API: {e}")



###################################################################################################################


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
""", unsafe_allow_html = True)


with st.container():
    st.markdown('<div class="login-box">', unsafe_allow_html = True)

    if st.session_state.page == "login":
        st.markdown("## 🔐 Login")
        
        username = st.text_input("User")
        password = st.text_input("Password", type = "password")
        
        if st.button("Sign in", use_container_width = True):
            login(username, password)
        
        st.button("Sign up", on_click = go_to_register, use_container_width = True)

    elif st.session_state.page == "register":
        st.markdown("## 📝 Sign up")
        
        new_username = st.text_input("New user")
        new_password = st.text_input("New password", type = "password")
        
        if st.button("Sign up", use_container_width = True):
            if new_username.strip() == "" or new_password.strip() == "":
                st.warning("Please fill in both fields.")
            else:
                register(new_username, new_password)
        
        st.button("Back to Login", on_click = go_to_login, use_container_width = True)

    elif st.session_state.page == "chat":
        st.markdown("## 🤖 Welcome to Chatbot!")
        st.success("Login successfully.")
        st.write("You are authenticated. Here you will enter the chatbot interface.")
        st.button("Exit", on_click = lambda: st.session_state.clear(), use_container_width = True)

    st.markdown('</div>', unsafe_allow_html = True)
