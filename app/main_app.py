import streamlit as st
from view.page_home import page_home
from view.page_chat import page_chat
from view.page_categoria import page_categoria


# Função para exibir a página de perfil
def page_profile():
    st.title("Perfil do Usuário")
    st.write("Esta é a página de perfil.")

# Função para exibir a página de configurações
def page_settings():
    st.title("Configurações")
    st.write("Esta é a página de configurações.")

# Função principal para renderizar a aplicação
def main():
    st.set_page_config(layout="wide")
    st.sidebar.title("Menu")
    options = ["Página Inicial", "Chat","Categorizacao de produtos", "Configurações"]
    menu = st.sidebar.selectbox("Selecione uma página", options)


    if menu == "Página Inicial":
        page_home()
    elif menu == "Chat":
        page_chat()
    elif menu == "Categorizacao de produtos":
        page_categoria()
    elif menu == "Configurações":
        page_settings()

if __name__ == "__main__":
    main()
