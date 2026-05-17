import streamlit as st


def verificar_acesso():
    """
    Controle simples de acesso por senha.

    No Streamlit Cloud:
    App > Settings > Secrets

    Exemplo:
    APP_PASSWORD = "sua_senha_aqui"
    """

    senha_configurada = st.secrets.get("APP_PASSWORD", "")

    if senha_configurada == "":
        st.error("Senha do sistema não configurada. Configure APP_PASSWORD nos Secrets do Streamlit.")
        st.stop()

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if st.session_state["autenticado"]:
        return

    st.title("🔐 Acesso restrito")

    senha_digitada = st.text_input(
        "Digite a senha para acessar o sistema",
        type="password"
    )

    entrar = st.button("Entrar")

    if entrar:
        if senha_digitada == senha_configurada:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")

    st.stop()


def sair():
    st.session_state["autenticado"] = False
    st.rerun()
