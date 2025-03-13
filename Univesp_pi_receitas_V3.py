import mysql.connector
import streamlit as st
import pandas as pd

# Conexão com o MySQL
conn = mysql.connector.connect(
    host='sql10.freesqldatabase.com',
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database='sql10767151' 
)

# Título da aplicação + Configuracao da Pagina
st.markdown(
    """
    <style>
    .center-image {display: flex;justify-content: center;align-items: center;
        margin-top: 20px;
        margin-bottom: 20px}
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

# Capa ("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQGXogBM6HJPQ-vSlzzx-uZkHQBjEO8h_7qVk_lY6-XaQ30Ru7-_CPQjGygGFojx4_hrsk&usqp=CAU")
# FAixa ("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQz-lpamw4E1xoaEa4JTwuZ9pk38L-8-fo-bg&s")

# Barra de entrada de texto
user_input = st.text_input("Digite nome do doce que se deseja consultar")

if user_input:
    cursor = conn.cursor()

    # Consulta SQL para obter os ingredientes
    query_ingredientes = f"""
        SELECT Ingredientes
        FROM Receitas
        WHERE UPPER(Nome) LIKE UPPER('%{user_input}%')
        LIMIT 10
    """
    cursor.execute(query_ingredientes)
    resultados_ingredientes = cursor.fetchall()

    # Exibir os resultados dos ingredientes
    if resultados_ingredientes:
        st.write("Principais Ingredientes e Medidas:")
        df_ingredientes = pd.DataFrame(resultados_ingredientes, columns=["Ingredientes"])
        st.table(df_ingredientes)
    else:
        st.write("Nenhum resultado encontrado para os ingredientes.")

    # Consulta SQL para obter o modo de preparo
    query_preparo = f"""
        SELECT Preparo
        FROM Receitas
        WHERE UPPER(Nome) LIKE UPPER('%{user_input}%')
        LIMIT 10
    """
    cursor.execute(query_preparo)
    resultados_preparo = cursor.fetchall()

    # Exibir os resultados do modo de preparo
    if resultados_preparo:
        st.write("Modo de Preparo:")
        df_preparo = pd.DataFrame(resultados_preparo, columns=["Preparo"])
        st.table(df_preparo)
    else:
        st.write("Nenhum resultado encontrado para o modo de preparo.")

    cursor.close()

conn.close()