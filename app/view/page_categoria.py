# pages/page_home.py

import streamlit as st
from controller.categoriaController import categoriaController
import pandas as pd
import logging
import openai
import mysql.connector
import requests
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os






def page_categoria():
    clCategoria = categoriaController()
    st.title("Categorização de produtos")

    opcao = st.radio("Escolha uma opção", ( "Predição de Categoria"
                                           ,"Upload de Arquivo CSV"
                                           ,"Lista categorias"
                                           , "Chat"))

    if opcao == "Predição de Categoria":
        titleProduct = st.text_input("Digite o Nome do item")
        if st.button("Salvar"):
            #TODO Adicionar validação para não enviar valor nulo
            response = clCategoria.categoriaAgent(titleProduct)
            titleProduct = ""
            st.write(f"Nome do item: {titleProduct}")
            st.write(f"Categoria Predita:")
            st.json(response)

    elif opcao == "Upload de Arquivo CSV":
        uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            for index , row in df.iterrows():
                response = clCategoria.categoriaAgent(row["produto"])
                st.write(f"Nome do item da linha {index}: {row['produto']}")
                st.write(f"Categoria Predita:")
                st.json(response)
            
             
            # st.subheader("Dados do arquivo CSV")
            # st.dataframe(df, use_container_width=None)
 
    elif opcao == "Lista categorias":
        
        categorias = clCategoria.get_all_categories()
        if categorias is None or not categorias:
            st.warning("Nenhuma categoria encontrada")
        else:
            df = pd.DataFrame(categorias)
            df = df.drop(columns=df.columns[0])
            df.columns = [
                "Produto",
                "Categoria nível 1",
                "Categoria nível 2",
                "Categoria nível 3",
                "Código NCM",
                "Data de Cadastro",
            ]
            st.subheader("Categorias casdastradas")
            df_reversed = df[::-1]
            st.dataframe(df_reversed, use_container_width=True)
            
            
    elif opcao =="Chat":
     



        st.subheader("Chat - Relatórios com linguagem natural")

        if 'historico' not in st.session_state:
            st.session_state.historico = []

        mensagem_usuario = st.text_input("Você:", key="mensagem_usuario")

        if st.button("Enviar"):
            if mensagem_usuario:
                #st.session_state.historico.append(f"Você: {mensagem_usuario}")
                st.write(f"Usuário : {mensagem_usuario} ") 
                consulta_sql = clCategoria.relatorioCategoriaAgent(mensagem_usuario)
                # st.session_state.historico.append(f"Consulta SQL gerada: {consulta_sql}")
                st.write(f"Consulta SQL gerada : {consulta_sql} ")
                resultados, colunas = clCategoria.executar_consulta_sql(consulta_sql)
                if colunas:
                    #TODO Quando realizado varias consultas o historico acaba adicionado sql que não deveria, ver como contronar isso
                    # st.session_state.historico.append(f"Resultados da consulta: {resultados}")
                    st.write("Resultados da consulta:")
                    st.write(pd.DataFrame(resultados, columns=colunas))
                else:
                    st.write("Nenhum registro encontrado")
                    # st.session_state.historico.append(resultados)

        for mensagem in st.session_state.historico:
            st.write(mensagem)