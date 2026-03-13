"""
Tela de Calendário de Reservas.
"""
import streamlit as st
import streamlit_calendar as st_cal
from database.supabase import fetch_reservas, fetch_veiculos, fetch_motoristas, clear_reservas_cache
from utils.formatters import criar_mapa_veiculos, criar_mapa_motoristas, exibir_reserva_no_calendario
from pages.styles import CALENDAR_CSS
from config.settings import CALENDAR_OPTIONS
from utils.date_utils import hoje


def renderizar():
    """Renderiza a tela de reservas."""
    st.title("Calendário de Reservas")
    
    # Busca dados
    dados_reservas = fetch_reservas()
    dados_veiculos = fetch_veiculos()
    dados_motoristas = fetch_motoristas()
    
    mapa_veiculos = criar_mapa_veiculos(dados_veiculos)
    mapa_motoristas = criar_mapa_motoristas(dados_motoristas)
    
    opcoes_veic = ["Todos"] + list(mapa_veiculos.keys())
    opcoes_mot = ["Todos"] + list(mapa_motoristas.keys())
    
    # Inicializa filtros
    if "filtro_data" not in st.session_state:
        st.session_state["filtro_data"] = hoje()
    if "filtro_veic" not in st.session_state:
        st.session_state["filtro_veic"] = "Todos"
    if "filtro_mot" not in st.session_state:
        st.session_state["filtro_mot"] = "Todos"
    
    def limpar_filtros():
        st.session_state["filtro_data"] = hoje()
        st.session_state["filtro_veic"] = "Todos"
        st.session_state["filtro_mot"] = "Todos"
    
    # Área de filtros
    with st.expander("🔍 Buscar e Filtrar", expanded=True):
        col_data, col_veic, col_mot, col_btn = st.columns([2, 2, 2, 1])
        
        with col_data:
            st.date_input("Ir para a data:", format="DD/MM/YYYY", key="filtro_data")
        
        with col_veic:
            st.selectbox(
                "Veículo",
                options=opcoes_veic,
                format_func=lambda x: "Todos" if x == "Todos" else mapa_veiculos[x],
                key="filtro_veic"
            )
        
        with col_mot:
            st.selectbox(
                "Motorista",
                options=opcoes_mot,
                format_func=lambda x: "Todos" if x == "Todos" else mapa_motoristas[x],
                key="filtro_mot"
            )
        
        with col_btn:
            st.write("")
            st.write("")
            st.button("🔄 Resetar", on_click=limpar_filtros, use_container_width=True)
    
    # Configuração do calendário
    opcoes_calendario = CALENDAR_OPTIONS.copy()
    opcoes_calendario["initialDate"] = str(st.session_state["filtro_data"])
    
    # Filtra e formata eventos
    eventos = exibir_reserva_no_calendario(
        dados_reservas,
        mapa_veiculos,
        mapa_motoristas,
        st.session_state["filtro_veic"],
        st.session_state["filtro_mot"]
    )
    
    # Renderiza calendário
    chave_dinamica = f"calendario_{st.session_state['filtro_data']}_{st.session_state['filtro_veic']}_{st.session_state['filtro_mot']}"
    
    state = st_cal.calendar(events=eventos, options=opcoes_calendario, custom_css=CALENDAR_CSS, key=chave_dinamica)
    
    if "eventClick" in state:
        from pages.components.components import mostrar_detalhes
        mostrar_detalhes(state["eventClick"])
    
    # Botão de nova reserva
    if st.button("**Cadastrar nova reserva**", icon="➕", type="secondary", use_container_width=True):
        st.session_state["pagina"] = "cadastro_reserva"
        st.rerun()
