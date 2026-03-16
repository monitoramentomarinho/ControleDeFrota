"""
Tela de Motoristas.
"""
import streamlit as st
import datetime
from streamlit_phone_number import st_phone_number
from database.supabase import (
    fetch_motoristas,
    fetch_reservas,
    insert_motorista,
    upload_imagem,
    clear_motoristas_cache,
)
from utils.formatters import extrair_numero_telefone, formatar_telefone_br
from pages.components.components import exibir_foto_motorista
from config.settings import STORAGE_MOTORISTAS_PATH


def renderizar():
    """Renderiza a tela de motoristas."""
    st.title("Página de Motoristas")
    
    dados_motoristas = fetch_motoristas()
    todas_reservas = fetch_reservas()
    
    # Exibir motoristas
    for motorista in dados_motoristas:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 1, 1], gap="medium")
            
            with col1:
                exibir_foto_motorista(motorista['Foto_perfil'])
            
            with col2:
                st.subheader(motorista["Nome"])
                st.write(f"ID: {motorista['id']}")
                
                telefone_exibicao = extrair_numero_telefone(motorista['Telefone'])
                st.write(f"Telefone: {telefone_exibicao}")
            
            with col3:
                st.write("Reserva atual:")
                reserva_atual = [r for r in todas_reservas if r.get("id_motorista") == motorista["id"]]
                
                if reserva_atual:
                    reserva = reserva_atual[0]
                    st.write(f"Motivo da locação: {reserva['motivo_locacao']}")
                    st.write(f"Data de início: {reserva['data_retirada']}")
                    st.write(f"Data de término: {reserva['data_devolucao']}")
                else:
                    st.write("Nenhuma reserva ativa.")
    
    # Formulário de novo motorista
    st.subheader("Cadastrar novo Motorista:")
    with st.form("Formulário de Motorista", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        telefone = st_phone_number("Telefone", default_country="BR")

        # Mostrar o telefone formatado enquanto o usuário digita
        telefone_formatado = formatar_telefone_br(extrair_numero_telefone(telefone))
        if telefone_formatado:
            st.markdown(f"**Telefone válido:** {telefone_formatado}")

        foto_perfil = st.file_uploader("Foto de Perfil", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("Salvar Motorista"):
            if nome and telefone and foto_perfil:
                try:
                    # Gera caminho único para a imagem
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    caminho_foto = f"{STORAGE_MOTORISTAS_PATH}/{timestamp}_{foto_perfil.name}"
                    
                    # Faz upload e obtém URL
                    bytes_foto = foto_perfil.getvalue()
                    url_foto = upload_imagem(caminho_foto, bytes_foto, foto_perfil.type)
                    
                    # Extrai número de telefone
                    numero_limpo = extrair_numero_telefone(telefone)
                    
                    # Insere no banco
                    novo_motorista = {
                        "Nome": nome,
                        "Telefone": numero_limpo,
                        "Foto_perfil": url_foto
                    }
                    
                    insert_motorista(novo_motorista)
                    clear_motoristas_cache()
                    st.success("Motorista cadastrado com sucesso!")
                    
                except Exception as e:
                    st.error(f"Erro ao salvar a foto ou cadastrar: {e}")
            else:
                st.error("Por favor, preencha todos os campos e envie uma foto.")
