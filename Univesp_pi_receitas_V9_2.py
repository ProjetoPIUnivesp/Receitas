#!/usr/bin/env python
# coding: utf-8

import pymysql
import streamlit as st
import pandas as pd

# Conexão com o MySQL
config = {
    'host':'sql.freedb.tech',
    'user':st.secrets['DB_USERNAME'],
    'password':st.secrets['DB_PASSWORD'],
    'database':'freedb_Receitas', 
    'charset':'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

conn = pymysql.connect(**config)

# Título da aplicação + Configuração da Página
st.markdown(
    """
    <style>
    .center-image {display: flex;justify-content: center;align-items: center;
        margin-top: 20px;
        margin-bottom: 20px}
    .video-container {
        position: relative;
        overflow: hidden;
        width: 100%;
        padding-top: 56.25%; /* 16:9 Aspect Ratio */
        margin: 20px 0;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .video-iframe {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        width: 100%;
        height: 100%;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: black;'>Receitas: Delícias da Tia Rosana</h1>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="center-image">
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQz-lpamw4E1xoaEa4JTwuZ9pk38L-8-fo-bg&s" alt="Logo" width="400">
    </div>
    """,
    unsafe_allow_html=True
)

# Barra lateral com botões
st.sidebar.title("Menu")
opcao = st.sidebar.radio("Selecione uma opção:", ("Consultar Receitas", "Inserir Nova Receita", "Deletar Receita"))

if opcao == "Consultar Receitas":
    # Barra de entrada de texto para consulta
    user_input = st.text_input("Digite o nome do doce que deseja consultar")

    if user_input:
        cursor = conn.cursor()

        # Consulta SQL para obter os ingredientes, preparo e link
        query = f"""
            SELECT Ingredientes, Preparo, link
            FROM Receitas
            WHERE UPPER(Nome) LIKE UPPER(REPLACE('%{user_input}%',' ',''))
            LIMIT 10
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        # Exibir os resultados
        if resultados:
            # Exibir ingredientes
            st.write("Principais Ingredientes e Medidas:")
            df_ingredientes = pd.DataFrame([r['Ingredientes'] for r in resultados], columns=["Ingredientes"])
            st.table(df_ingredientes)

            # Exibir modo de preparo
            st.write("Modo de Preparo:")
            df_preparo = pd.DataFrame([r['Preparo'] for r in resultados], columns=["Preparo"])
            st.table(df_preparo)
            
            # INSERIR O VÍDEO DO YOUTUBE APÓS O MODO DE PREPARO
            st.markdown("---")
            st.markdown("### 🎥 Vídeo da Receita")
            
            # Obter o link do YouTube do banco de dados
            youtube_link = resultados[0]['link']
            
            # Extrair o ID do vídeo do link do YouTube (caso necessário)
            # Se o link já estiver no formato embed, usar diretamente
            if 'embed' in youtube_link:
                embed_link = youtube_link
            else:
                # Extrair ID do vídeo de links padrão do YouTube
                video_id = youtube_link.split('v=')[-1].split('&')[0]
                embed_link = f"https://www.youtube.com/embed/{video_id}"
            
            # Container responsivo para o vídeo do YouTube
            st.markdown(
                f"""
                <div class="video-container">
                    <iframe class="video-iframe" src="{embed_link}" 
                    title="Receita da Tia Rosana" frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen></iframe>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
        else:
            st.write("Nenhum resultado encontrado.")

        cursor.close()

elif opcao == "Inserir Nova Receita":
    st.subheader("Inserir Nova Receita")

    # Formulário para inserção de dados
    with st.form(key="form_inserir_receita"):
        nome_receita = st.text_input("Nome da Receita")
        ingredientes = st.text_area("Ingredientes (separados por vírgula)")
        preparo = st.text_area("Modo de Preparo")
        link_youtube = st.text_input("Link do YouTube")

        botao_inserir = st.form_submit_button("Inserir Receita")

        if botao_inserir:
            if nome_receita and ingredientes and preparo:
                cursor = conn.cursor()

                # Inserção no banco de dados
                query_inserir = f"""
                    INSERT INTO Receitas (Nome, Ingredientes, Preparo, link)
                    VALUES ('{nome_receita}', '{ingredientes}', '{preparo}', '{link_youtube}')
                """
                cursor.execute(query_inserir)
                conn.commit()

                st.success("Receita inserida com sucesso!")
                cursor.close()
            else:
                st.error("Por favor, preencha todos os campos obrigatórios.")

elif opcao == "Deletar Receita":
    st.subheader("Deletar Receita")

    # Formulário para inserção de dados
    with st.form(key="form_deletar_receita"):
        nome_receita = st.text_input("Nome da Receita")
        botao_deletar = st.form_submit_button("Deletar Receita")

        if botao_deletar:
            if nome_receita:
                cursor = conn.cursor()

                # Deletar no banco de dados
                query_deletar = f"""
                    DELETE FROM Receitas
                    WHERE UPPER(Nome) LIKE UPPER(REPLACE('%{nome_receita}%',' ',''));
                """
                cursor.execute(query_deletar)
                conn.commit()

                st.success("Receita deleta com sucesso!")
                cursor.close()
            else:
                st.error("Por favor, preencha novamente os campos.")
                
# Fechar a conexão com o banco de dados
