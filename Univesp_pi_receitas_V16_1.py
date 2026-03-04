import pymysql
import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import requests
from urllib.parse import quote

# Configurações de login (definidas diretamente no código)
USUARIO_CORRETO = st.secrets['CD_USERNAME']
SENHA_CORRETA = st.secrets['CD_PASSWORD']

# Configuração da API Google Gemini
API_KEY = st.secrets['API_TOKEN_CD']
genai.configure(api_key=API_KEY)

# Função para consultar a IA (adaptada para UMA ÚNICA chamada)
def consultar_ia_para_receita(nome_receita):
    # Prompt único solicitando todas as informações em formato estruturado
    prompt_unico = f"""
    Para a receita do doce chamado "{nome_receita}", forneça as seguintes informações em formato JSON válido:
    
    1. ingredientes: lista dos principais ingredientes com medidas (máximo 200 caracteres)
    2. preparo: modo de preparo simples, susinto e resumido sem palavras incompletas (máximo 200 caracteres)
    
    Retorne APENAS o JSON, sem texto adicional, sem formatação markdown, seguindo exatamente este formato:
    {{"ingredientes": "texto aqui", "preparo": "texto aqui"}}
    """
    
    resultado = {'ingredientes': '','preparo': ''}
    
    try:
        # ÚNICA chamada à API
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(prompt_unico)
        
        if response and hasattr(response, 'text'):
            resposta_texto = response.text.strip()
            
            # Limpar possíveis marcações markdown (```json ```)
            if resposta_texto.startswith('```json'):
                resposta_texto = resposta_texto.replace('```json', '').replace('```', '').strip()
            elif resposta_texto.startswith('```'):
                resposta_texto = resposta_texto.replace('```', '').strip()
            
            # Tentar fazer o parse do JSON
            try:
                dados_json = json.loads(resposta_texto)
                
                # Extrair os dados do JSON
                resultado['ingredientes'] = dados_json.get('ingredientes', '')[:200]
                resultado['preparo'] = dados_json.get('preparo', '')[:200]
                
            except json.JSONDecodeError:
                # Fallback: se não conseguir fazer parse do JSON, tenta extrair manualmente
                linhas = resposta_texto.split('\n')
                for linha in linhas:
                    if 'ingredientes' in linha.lower() and ':' in linha:
                        resultado['ingredientes'] = linha.split(':', 1)[1].strip()[:200]
                    elif 'preparo' in linha.lower() and ':' in linha:
                        resultado['preparo'] = linha.split(':', 1)[1].strip()[:200]
        else:
            resultado['ingredientes'] = "Não foi possível obter os ingredientes"
            resultado['preparo'] = "Não foi possível obter o modo de preparo"
            
        return resultado
        
    except Exception as e:
        return {
            'ingredientes': f"Erro na conexão com IA: {str(e)}",
            'preparo': "Erro na consulta"
        }

# Função para buscar vídeo no YouTube e extrair o ID
def buscar_video_youtube(consulta):
    try:
        # Codificar a consulta para URL
        consulta_codificada = quote(consulta)
        
        # Fazer requisição para a página de pesquisa do YouTube
        url = f"https://www.youtube.com/results?search_query={consulta_codificada}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Procurar pelo padrão de ID de vídeo no HTML
            import re
            # Padrão para encontrar IDs de vídeo no YouTube
            pattern = r'"videoId":"([^"]+)"'
            matches = re.findall(pattern, response.text)
            
            if matches:
                # Retornar o primeiro ID de vídeo encontrado
                return matches[0]
    except Exception as e:
        st.error(f"Erro ao buscar vídeo: {str(e)}")
    
    return None

# Verificar se o usuário está logado
def verificar_login():
    if "logado" not in st.session_state:
        st.session_state.logado = False
    
    if not st.session_state.logado:
        # Tela de login
        st.markdown("<h1 style='text-align: center; color: black;'>Receitas: Delícias da Tia Rosana</h1>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="center-image">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQz-lpamw4E1xoaEa4JTwuZ9pk38L-8-fo-bg&s" alt="Logo" width="400">
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("### 🔐 Login de Acesso")
        
        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            enviar = st.form_submit_button("Entrar")
            
            if enviar:
                if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
                    st.session_state.logado = True
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos!")
        
        return False
    else:
        return True

# Conexão com o MySQL
config = {
    'host': 'sql.freedb.tech',
    'user':st.secrets['DB_USERNAME'],
    'password':st.secrets['DB_PASSWORD'],
    'database': 'freedb_freedb_Receitas',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

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

# Verificar login antes de mostrar o conteúdo principal
if verificar_login():
    conn = pymysql.connect(**config)

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
    
    # Botão de logout na barra lateral
    if st.sidebar.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()
    
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
                # Quando não encontra no banco, consulta a IA (AGORA APENAS 1 CHAMADA)
                st.warning(f"Não encontramos '{user_input}' no nosso banco de receitas. Consultando inteligência artificial...")
                
                with st.spinner('Consultando IA...'):
                    resposta_ia = consultar_ia_para_receita(user_input)  # ÚNICA chamada
                
                # Exibir no layout das receitas do banco de dados
                st.write("Principais Ingredientes e Medidas:")
                df_ingredientes_ia = pd.DataFrame([resposta_ia['ingredientes']], columns=["Ingredientes"])
                st.table(df_ingredientes_ia)

                st.write("Modo de Preparo:")
                df_preparo_ia = pd.DataFrame([resposta_ia['preparo']], columns=["Preparo"])
                st.table(df_preparo_ia)
                
                # Manter a seção de vídeo para consistência visual
                st.markdown("---")
                st.markdown("### 🎥 Vídeo da Receita")

                # CORREÇÃO: Buscar vídeo no YouTube e incorporar diretamente
                consulta = f"Receita de doce {user_input} brasileira ptbr"
                
                with st.spinner('Buscando vídeo no YouTube...'):
                    video_id = buscar_video_youtube(consulta)
                
                if video_id:
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
                    st.info("Não foi possível encontrar um vídeo para esta receita no YouTube.")

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

    conn.close()

