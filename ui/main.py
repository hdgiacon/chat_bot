import streamlit as st
import time


if st.session_state.get("session_expired", False):
    st.warning("🔒 Your session has expired. Please log in again.")
    
    st.session_state["session_expired"] = False 
    
    time.sleep(2)


st.switch_page("pages/login.py")