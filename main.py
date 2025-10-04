import streamlit as st

from config import *
from src.prompt_llm import prompt_llm
from src.search import _web_search_prettify_
from src.vectors_data import setup_vectors, vectors_search

def app():
    

    st.markdown(
    """
    <style>
        .stAppDeployButton {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True
    )

    # Konfiguracija stranice
    st.set_page_config(
        page_title="Pitanje-Odgovor Sajt",
        page_icon="🤖",
        layout="centered"
    )

    # Pozadinska slika
    page_bg_img = """
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                        url("https://i.pinimg.com/1200x/da/5b/04/da5b046c985324002dea17f65905e34b.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

    # Naslov
    st.markdown("""
    <div style='text-align: center; padding-top: 20px; padding-bottom: 10px;'>
        <h1 style='font-size: 64px; color: white; margin-bottom: 10px;'> AI Asistent</h1>
        <h3 style='color: lightgray; margin-top: 0;'>Tu sam da odgovorim — šta te zanima?</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Inicijalizacija session_state
    if "user_question" not in st.session_state:
        st.session_state.user_question = ""
    if "answer" not in st.session_state:
        st.session_state.answer = ""

    # Callback za brisanje
    def clear_all():
        st.session_state.user_question = ""
        st.session_state.answer = ""

    # Input box
    st.markdown("<h3>❓ <span style='color: #FFFFFF;'>Vaše pitanje:</span></h3>", unsafe_allow_html=True)
    user_question = st.text_area(
        label="Unesite vaše pitanje:",
        placeholder="Ovde unesite vaše pitanje...",
        height=100,
        key="user_question"
    )

    # Output box
    st.markdown("<h3>💬 <span style='color: #FFFFFF;'>Odgovor:</span></h3>", unsafe_allow_html=True)

    if len(st.session_state.user_question) and st.session_state.user_question.strip():
        # ovde ide tvoj stvarni odgovor (npr. poziv modela)
        
        context = _web_search_prettify_(_user_prompt=user_question, _results=WEB_SEARCH_VALID_URLS_NUM)

        vectors = setup_vectors(context)
        url_text = vectors_search(query=user_question, data=vectors, k=WEB_SEARCH_VALID_URLS_NUM)
        text = ""

        for url, tx in url_text.items():
            for t in tx:
                text.join("\n\n"+ t)

        answer = prompt_llm(user_prompt=user_question, context_text=text, api_key=LLM_API_KEY)
        # answer = "test"
        st.markdown(f"""
            <div style='background-color: rgba(255,255,255,0.15); padding: 20px; border-radius: 10px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.3); margin-top: 10px;'>
                <p style='color: white; font-size: 18px;'>✅ {answer}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <hr style='margin-top: 30px; margin-bottom: 10px;'>
            <p style='color: lightgray; font-size: 16px; text-align: center;'>
            🤖 Ako te još nešto zanima, slobodno postavi novo pitanje. Tu sam da pomognem.
            </p>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Molimo unesite pitanje u polje iznad da biste dobili odgovor.")

    # Dugme za brisanje — OVDE se pojavljuje (ispod output boxa)
    st.markdown("---")
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        # koristimo on_click callback — ovo rešava StreamlitAPIException
        st.button("🗑️ Obriši sve", on_click=clear_all, use_container_width=True)


if __name__ == "__main__":
    app()
