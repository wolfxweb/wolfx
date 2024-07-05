import streamlit as st
from PyPDF2 import PdfReader
from langchain import OpenAI, LLMChain

# Definir a chave da API diretamente
openai_api_key = "sk-proj-D8EMezj2OAP7g6TwPUbcT3BlbkFJ9278Lgz7j7NKKzlruZDq"

# Inicializar LangChain com o modelo ChatGPT-4 Turbo da OpenAI
openai = OpenAI(api_key=openai_api_key)
llm = LLMChain(llm=openai, model="text-davinci-003")

# Classe de template para categorização de PDF
class TemplatePdf:
    def __init__(self):
        self.system_template = """
            Chamado: 68335

            Você é especialista em análise de requisitos de software, o usuário informa um texto com os requisitos e você organiza em tarefas a serem executadas.
            Considere os títulos como tarefas, e a área de alteração o que deve ser feito para palavras como inserir, alterar e deletar. Crie
            SQL para banco de dados PostgreSQL como exemplo, caso contrário, crie um exemplo para PHP.

            Exemplo de resposta esperada:
            - Criar scripts: Script para adicionar as colunas REA_COPIAR_TRIAGEM e REA_COPIAR_COTACAO na tabela REGRA_APROVACAO.
            Código de exemplo: ALTER TABLE REGRA_APROVACAO ADD REA_COPIAR_TRIAGEM CHAR(1) DEFAULT 'N', ADD REA_COPIAR_COTACAO CHAR(1) DEFAULT 'N';

            - Ajustar processamento do erro do pedido: O e-mail deverá ser enviado somente se o usuário solicitante tem permissão para alterar compras (coluna UPF_ALTERAR_COMPRA da tabela USU_PERMISSAO com valor “M”, ou “R”).
            Código de exemplo:
            if ($valorUpf === 'M') {
                // Enviar e-mail apenas ao solicitante
                // Implementação do envio de e-mail aqui
            } elseif ($valorUpf === 'R' && $tipoCompra === 'Registro') {
                // Verificar se a compra é de registro antes de enviar e-mail ao solicitante
                // Implementação do envio de e-mail aqui
            } elseif ($valorUpf === 'Q') {
                // Não enviar e-mail
                // Nenhuma ação necessária
            } else {
                // Valor UPF desconhecido
                // Tratamento de erro ou exceção, conforme necessário
            }
        """

# Interface do Streamlit
st.title("Processamento de PDF com ChatGPT-4 Turbo")

uploaded_file = st.file_uploader("Faça upload do seu arquivo PDF", type="pdf")

if uploaded_file is not None:
    # Função para extrair texto do PDF
    def extract_text_from_pdf(pdf):
        pdf_reader = PdfReader(pdf)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text

    # Função para limitar o tamanho do texto dentro do limite de tokens
    def limit_text_size(text, max_tokens=8192):
        # Limitar o tamanho do texto para não exceder o máximo permitido
        if len(text.split()) > max_tokens:
            text = ' '.join(text.split()[:max_tokens])
        return text

    # Ler e extrair texto do PDF
    pdf_text = extract_text_from_pdf(uploaded_file)

    # Dividir o texto em partes menores para respeitar o limite de tokens
    tokens_per_chunk = 8000  # Ajuste conforme necessário para respeitar o limite
    chunks = [pdf_text[i:i + tokens_per_chunk] for i in range(0, len(pdf_text), tokens_per_chunk)]

    # Processar cada parte do texto usando LangChain e ChatGPT-4 Turbo
    for i, chunk in enumerate(chunks):
        chunk = limit_text_size(chunk)
        template = TemplatePdf().system_template.format(text=chunk)
        try:
            response = llm.run(prompt=template)
            st.write(f"Parte {i + 1}:")
            st.write(response.choices[0].text.strip())
        except Exception as e:
            st.error(f"Erro ao processar texto do PDF: {str(e)}")
