import streamlit as st
import datetime
import io
from PIL import Image

# Importando as funções do banco de dados (já preparadas no supabase.py)
from database.supabase import (
    fetch_veiculos, 
    fetch_motoristas, 
    fetch_reservas, 
    upload_imagem, 
    delete_reserva, 
    clear_reservas_cache, 
    clear_veiculos_cache,
    sincronizar_status_veiculo
)
from utils.formatters import criar_mapa_veiculos, criar_mapa_motoristas


def comprimir_imagem(imagem_bytes, qualidade=60):
    """Reduz o tamanho e a qualidade da imagem para economizar muito espaço no Supabase."""
    # Abre a imagem usando a biblioteca Pillow
    img = Image.open(io.BytesIO(imagem_bytes))
    
    # Se a imagem for PNG (fundo transparente), converte para RGB para poder salvar como JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    # Redimensiona a imagem caso ela seja gigantesca (ex: câmeras de 108MP)
    max_size = (1280, 1280)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    # Salva no formato JPEG com a qualidade reduzida
    img.save(output, format="JPEG", quality=qualidade)
    
    return output.getvalue()


def renderizar():
    """Renderiza a tela de devolução."""
    st.title("Devolução de Veículos")
    st.write("Aqui você pode registrar a devolução dos veículos reservados.")

    reservas = fetch_reservas()
    dados_veiculos = fetch_veiculos()
    dados_motoristas = fetch_motoristas()

    mapa_veiculos = criar_mapa_veiculos(dados_veiculos)
    mapa_motoristas = criar_mapa_motoristas(dados_motoristas)

    # Inicializa session_state para controlar o formulário
    if "reserva_devolucao" not in st.session_state:
        st.session_state.reserva_devolucao = None

    # Verifica se uma reserva foi selecionada para devolução
    if st.session_state.reserva_devolucao is None:
        # Exibe a lista de reservas
        for reserva in reservas:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{reserva['motivo_locacao']}**: {mapa_veiculos.get(reserva['Veiculo_id'], 'Desconhecido')} reservado por {mapa_motoristas.get(reserva['id_motorista'], 'Desconhecido')}")
                with col2:
                    if st.button(type="primary", label="Devolver", key=f"devolver_{reserva['id']}", use_container_width=True):
                        st.session_state.reserva_devolucao = reserva
                        st.rerun()
    else:
        # Exibe o formulário de devolução
        reserva_selecionada = st.session_state.reserva_devolucao
        st.subheader(f"Devolução - {reserva_selecionada['motivo_locacao']}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Veículo:** {mapa_veiculos.get(reserva_selecionada['Veiculo_id'], 'Desconhecido')}")
            st.write(f"**Motorista:** {mapa_motoristas.get(reserva_selecionada['id_motorista'], 'Desconhecido')}")
        with col2:
            if st.button("Voltar", use_container_width=True):
                st.session_state.reserva_devolucao = None
                st.rerun()
        
        # Formulário de devolução
        with st.form("Formulário de Devolução", clear_on_submit=False):
            st.write("Preencha os dados da devolução:")
            nivel_combustivel = st.radio("Nível de Combustível:", options=["Cheio", "1/2", "1/4", "Reserva"])
            
            # Campos de fotos
            foto_t = st.file_uploader("Foto do Veículo (Traseira)", type=["jpg", "jpeg", "png"])
            foto_f = st.file_uploader("Foto do Veículo (Frontal)", type=["jpg", "jpeg", "png"])
            foto_ld = st.file_uploader("Foto do Veículo (Lateral Direita)", type=["jpg", "jpeg", "png"])
            foto_le = st.file_uploader("Foto do Veículo (Lateral Esquerda)", type=["jpg", "jpeg", "png"])

            if st.form_submit_button("Registrar Devolução", type="primary"):
                
                # Agrupa as fotos preenchidas
                fotos_para_enviar = [
                    ("Traseira", foto_t),
                    ("Frontal", foto_f),
                    ("Lateral_Direita", foto_ld),
                    ("Lateral_Esquerda", foto_le)
                ]
                
                # Pega apenas as fotos que o usuário realmente fez upload
                fotos_validas = [(nome, f) for nome, f in fotos_para_enviar if f is not None]
                
                if len(fotos_validas) > 0:
                    with st.spinner("Comprimindo e enviando imagens para o banco..."):
                        try:
                            # Timestamp para não sobrescrever arquivos no Supabase
                            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                            
                            # Loop para comprimir e enviar cada foto
                            for nome_foto, arquivo in fotos_validas:
                                
                                # 1. Aplica a compressão que criamos
                                bytes_comprimidos = comprimir_imagem(arquivo.getvalue())
                                
                                # 2. Define a pasta e o nome do arquivo no Storage do Supabase
                                caminho_storage = f"devolucoes/reserva_{reserva_selecionada['id']}_{nome_foto}_{timestamp}.jpg"
                                
                                # 3. Faz o upload (O Supabase vai colocar dentro da pasta 'devolucoes' no bucket 'Imagens')
                                upload_imagem(caminho_storage, bytes_comprimidos, "image/jpeg")
                            
                            # ==========================================
                            # CONCLUSÃO DA DEVOLUÇÃO
                            # ==========================================
                            veiculo_id = reserva_selecionada['Veiculo_id']
                            
                            # Deleta a reserva (ou atualiza o status, dependendo de como funciona o seu BD)
                            delete_reserva(reserva_selecionada['id'])
                            
                            # Limpa os caches para o sistema perceber as alterações instantaneamente
                            clear_reservas_cache()
                            clear_veiculos_cache()
                            
                            # Libera o veículo para "Disponível" novamente
                            sincronizar_status_veiculo(veiculo_id)
                            
                            st.success("Devolução concluída com sucesso! Fotos salvas com tamanho reduzido.")
                            st.session_state.reserva_devolucao = None
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Erro ao processar devolução: {e}")
                else:
                    st.error("Por favor, envie pelo menos uma foto para vistoria.")