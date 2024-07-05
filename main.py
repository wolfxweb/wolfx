# main.py

import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import bcrypt
from PIL import Image

# Configuração do banco de dados SQLite
DATABASE_URL = "sqlite:///blog.db"

# Criar uma conexão com o banco de dados
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()


# Definir a estrutura da tabela
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    content = Column(String)
    image = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    posted_at = Column(DateTime)


# Ligando a engine ao declarative base
Base.metadata.create_all(bind=engine)


# Função para cadastro de usuário
def signup(session):
    st.subheader("Cadastro")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    confirm_password = st.text_input("Confirmar Senha", type="password")

    if password != confirm_password:
        st.warning("As senhas não coincidem.")
        return

    if st.button("Cadastrar"):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(email=email, password=hashed_password)
        session.add(new_user)
        session.commit()
        st.success("Cadastro realizado com sucesso! Faça o login para acessar.")
        st.experimental_rerun()


# Função para login
def login(session):
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Login"):
        user = session.query(User).filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            st.success(f"Login bem sucedido como {email}.")
            return user
        else:
            st.error("Email ou senha incorretos.")
            return None


# Função para recuperação de senha (simulada)
def reset_password():
    st.subheader("Recuperar Senha")
    email = st.text_input("Email")

    if st.button("Enviar"):
        # Simular envio de e-mail de recuperação (poderia enviar um e-mail real usando um serviço de e-mail)
        st.success("Instruções para recuperação de senha enviadas para seu e-mail.")


# Função para adicionar ou editar um post
def edit_post(session):
    st.subheader("Criar/Editar Post")
    title = st.text_input("Título do Post")
    category = st.selectbox("Categoria", ["Tecnologia", "Esportes", "Entretenimento", "Outros"])
    content = st.text_area("Conteúdo do Post")
    uploaded_image = st.file_uploader("Carregar Imagem")

    if st.button("Salvar"):
        if uploaded_image is not None:
            # Salvar a imagem no sistema de arquivos
            image = Image.open(uploaded_image)
            image_path = f"uploads/{title}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            image.save(image_path)
        else:
            image_path = None

        # Adicionar o novo post ao banco de dados
        new_post = Post(title=title, category=category, content=content, image=image_path, posted_at=datetime.now())
        session.add(new_post)
        session.commit()
        st.success("Post salvo com sucesso!")
        st.experimental_rerun()


# Função para listar os posts com filtros
def list_posts(session):
    st.subheader("Lista de Posts")

    # Filtros
    search_term = st.text_input("Pesquisar por título")
    category_filter = st.selectbox("Filtrar por Categoria", ["", "Tecnologia", "Esportes", "Entretenimento", "Outros"])
    start_date = st.date_input("De data")
    end_date = st.date_input("Até data", datetime.today())

    # Consulta no banco de dados
    filtered_posts = session.query(Post).filter(
        Post.title.contains(search_term) if search_term else True,
        Post.category == category_filter if category_filter else True,
        Post.created_at >= start_date,
        Post.created_at <= end_date
    ).order_by(Post.created_at.desc()).all()

    # Mostrar os posts filtrados
    if filtered_posts:
        for post in filtered_posts:
            st.write(f"**{post.title}** - {post.posted_at.strftime('%d/%m/%Y')}")
            st.write(f"Categoria: {post.category}")
            st.write(post.content)
            if post.image:
                st.image(post.image, caption="Imagem do Post", use_column_width=True)
            st.write(f"Criado em: {post.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
            st.write("---")
    else:
        st.info("Nenhum post encontrado com os filtros selecionados.")


# Interface principal
def main():
    st.title("Blog com Streamlit e SQLAlchemy")

    Session = sessionmaker(bind=engine)
    session = Session()

    # Verificar se o usuário está logado
    if 'user' not in st.session_state:
        st.session_state.user = None

    st.sidebar.title("Menu")

    if st.session_state.user:
        menu = st.sidebar.radio("Selecione uma opção", ["Logout", "Criar/Editar Post", "Listar Posts"])
    else:
        menu = st.sidebar.radio("Selecione uma opção", ["Login", "Cadastro", "Recuperar Senha"])

    if menu == "Cadastro":
        signup(session)
    elif menu == "Login":
        st.session_state.user = login(session)
        if st.session_state.user:
            st.experimental_rerun()
    elif menu == "Recuperar Senha":
        reset_password()
    elif menu == "Criar/Editar Post" and st.session_state.user:
        edit_post(session)
    elif menu == "Listar Posts":
        list_posts(session)


if __name__ == "__main__":
    main()
