import streamlit as st
from database.supabase import fetch_veiculos, fetch_motoristas, fetch_reservas
from utils.formatters import criar_mapa_veiculos, criar_mapa_motoristas, filtrar_reservas


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
            with st.container(border=True, width="content"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{reserva['motivo_locacao']}: {mapa_veiculos.get(reserva['Veiculo_id'], 'Desconhecido')} reservado por {mapa_motoristas.get(reserva['id_motorista'], 'Desconhecido')}")
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
            st.write(f"Veículo: {mapa_veiculos.get(reserva_selecionada['Veiculo_id'], 'Desconhecido')}")
            st.write(f"Motorista: {mapa_motoristas.get(reserva_selecionada['id_motorista'], 'Desconhecido')}")
        with col2:
            if st.button("Voltar", use_container_width=True):
                st.session_state.reserva_devolucao = None
                st.rerun()
        
        
        # Formulário de devolução
        with st.form("Formulário de Devolução", clear_on_submit=False):
            st.write("Preencha os dados da devolução:")
            st.radio("Nivel de Combustível:", options=["Cheio", "1/2", "1/4", "Reserva"], key="nivel_combustivel")
            #Inserir fotos para adicionar no Google Drive#
            st.file_uploader("Foto do Veículo (Traseira)", accept_multiple_files=False, type=["jpg", "jpeg", "png"], key="fotos_traseira_devolucao")
            st.file_uploader("Foto do Veículo (Frontal)", accept_multiple_files=False, type=["jpg", "jpeg", "png"], key="fotos_frontal_devolucao")
            st.file_uploader("Foto do Veículo (Lateral Direita)", accept_multiple_files=False, type=["jpg", "jpeg", "png"], key="fotos_lateral_direita_devolucao")
            st.file_uploader("Foto do Veículo (Lateral Esquerda)", accept_multiple_files=False, type=["jpg", "jpeg", "png"], key="fotos_lateral_esquerda_devolucao")

            st.form_submit_button("Registrar Devolução", type="primary")

