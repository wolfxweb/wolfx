# pages/page_home.py

import streamlit as st
from controller.categoriaController import categoriaController
import pandas as pd
import logging

def page_categoria():
    clCategoria = categoriaController()
    st.title("Categorização de produtos")

    opcao = st.radio("Escolha uma opção", ("Predição de Categoria", "Upload de Arquivo CSV"))

    if opcao == "Predição de Categoria":
        titleProduct = st.text_input("Digite o Nome do item")
        if st.button("Salvar"):
            response = clCategoria.categoriaAgent(titleProduct)
            titleProduct = ""
            st.write(f"Nome do item: {titleProduct}")
            st.write(f"Categoria Predita:")
            st.json(response)

    elif opcao == "Upload de Arquivo CSV":
        uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.subheader("Dados do arquivo CSV")
            st.dataframe(df, width=None)


    categorias = clCategoria.get_all_categories()
    if categorias is None or not categorias:
        st.warning("Nenhuma categoria encontrada")
    else:
        df = pd.DataFrame(categorias)
        df = df.drop(columns=df.columns[0])
        df.columns = [
            "Nome do item",
            "Categoria nível 1",
            "Categoria nível 2",
            "Categoria nível 3",
            "Código NCM",
            "Data de Cadastro",
        ]
        st.subheader("Categorias casdastradas")
        df_reversed = df[::-1]
        st.dataframe(df_reversed, use_container_width=True)
