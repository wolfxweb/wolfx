from langchain.llms import OpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
import openai
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain
import mysql.connector
import logging
import json
from langchain.prompts import PromptTemplate
logging.basicConfig(level=logging.INFO)

#TODO Separar o agente do controller
class CategoriaTemplate:
    def __init__(self):
        #TODO Não vai ter o CANE rever o promt
        self.system_template = """
            Você é especialista em categorização de produtos, sua função é examinar cuidadosamente cada item e definir três níveis de categorias com precisão. 
            Durante o desempenho das suas atividades, analise detalhadamente as características e o contexto de cada produto para determinar os níveis de categorias mais apropriados.
            Na sua resposta, é fundamental incluir o NCM (Nomenclatura Comum do Mercosul) do produto.
            É essencial que você realize a análise com calma e atenção as informações passada, garantindo sempre que as três categorias estejam corretamente definidas.

            Exemplo de resposta esperada: 
             - categoria_principal: Ferramentas
             - categoria_secundaria: Fixadores
             - categoria_terciaria: Parafusos
             - ncm: 32091010  - informações_do_ncm: Esse cód
        """

        self.human_template = """
        ####{request}####
        """
        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template)
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["request"]
        )
        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )


class AgentCategoria:
    def __init__(
            self,
            open_ai_api_key,
            model='gpt-3.5-turbo',
            temperature=0,
            verbose=True
    ):
        self.logger = logging.getLogger(__name__)
        if verbose:
            self.logger.setLevel(logging.INFO)

        self._openai_key = open_ai_api_key
        self.chat_model = ChatOpenAI(model=model,
                                     temperature=temperature,
                                     openai_api_key=self._openai_key)
        self.verbose = verbose

    def getCategoria(self, text):
        categoria_template = CategoriaTemplate()

        categoria_agent = LLMChain(
            llm=self.chat_model,
            prompt=categoria_template.chat_prompt,
            verbose=self.verbose,
            output_key='agent_categoria_response'
        )

        overall_chain = SequentialChain(
            chains=[categoria_agent],
            input_variables=["request"],
            output_variables=["agent_categoria_response"],
            verbose=self.verbose
        )

        response = overall_chain(
            {"request": text},
            return_only_outputs=True
        )

        #TODO Ajsutar o template da categoria para retornar json  e depois remova esta parte que criar o json
        response_data = response["agent_categoria_response"].strip().replace("\n", " ")

        categorias = response_data.split(" - ")

        response_formatado = {}

        for categoria in categorias:
            key_value = categoria.split(": ", 1)
            key = key_value[0].strip().replace("-", "")
            value = key_value[1].strip().replace('\\"', '').replace('\\v', 'v').replace('"', '').replace("'",
                                                                                                         "").replace(
                "\\", "") if len(key_value) > 1 else ""
            response_formatado[key] = value

        response_formatado = {k.strip(): v for k, v in response_formatado.items()}

        return response_formatado
class categoriaController:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_connection = mysql.connector.connect(
            host="mysql",  # Nome do serviço do MySQL definido no Docker Compose
            user="root",
            password="root",
            database="wolfx_bd"
        )

    def categoriaAgent(self, text):
        #TODO Pegar o tocken do .env
        agent = AgentCategoria(open_ai_api_key="sk-proj-D8EMezj2OAP7g6TwPUbcT3BlbkFJ9278Lgz7j7NKKzlruZDq")
        response = agent.getCategoria(text)
        self.save_categoria(response,text)
        return response

    def save_categoria(self, data,text):
        #TODO Ajsuta para não adiconar caso não encontre uma categoria
        #TODO Analisar o cadastramento de itens duplicado, 
        cursor = self.db_connection.cursor()
        sql = """INSERT INTO categorias (categoria_1, categoria_2, categoria_3, ncm, produto)
                   VALUES (%s, %s, %s, %s,%s)"""
        values = (
            data.get("categoria_principal"),
            data.get("categoria_secundaria"),
            data.get("categoria_terciaria"),
            data.get("ncm"),
            text
        )
        cursor.execute(sql, values)
        self.db_connection.commit()
        cursor.close()

    def get_all_categories(self):
        cursor = self.db_connection.cursor(dictionary=True)
        sql = "SELECT * FROM categorias"
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def executar_consulta_sql(self,query):
            try:
                cursor = self.db_connection.cursor(dictionary=True)
                cursor.execute(query)
                resultados = cursor.fetchall()
                colunas = cursor.column_names
                cursor.close()
                return resultados, colunas
            except mysql.connector.Error as err:
                return f"Erro: {err}", []
            
    def relatorioCategoriaAgent(self,mensagem_usuario):
            #TODO Em algum momentos ele cria o sql correto mas com formato errado implementar validação do sql criado       
            #TODO Como tratar consultas de colunas que não são encontradas
            #TODO Refatorar a classe template da categoria para poder ter mais de um template           
            prompt_template = PromptTemplate.from_template("""
            Utilize a tabela `categorias` do banco de dados que contém as colunas `id`, `produto`, `categoria_1`, `categoria_2`, `categoria_3`,
            `ncn`,`categoria_terciaria`,e `data_cadastro`.
            gere sempre um unico sql,
            
            Gere uma consulta SQL com base na seguinte solicitação do usuário:
            
            {mensagem_usuario}
            """)
        
            #TODO Refatorar para classe agente da categoria
            openai.api_key = 'sk-proj-D8EMezj2OAP7g6TwPUbcT3BlbkFJ9278Lgz7j7NKKzlruZDq' 
            llm = OpenAI(api_key=openai.api_key)
            chain = LLMChain(llm=llm, prompt=prompt_template)
            consulta_sql = chain.run(mensagem_usuario)
            return consulta_sql