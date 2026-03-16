"""
Tela de Calendário de Reservas.
"""
import streamlit as st
import streamlit_calendar as st_cal
from database.supabase import fetch_reservas, fetch_veiculos, fetch_motoristas, clear_reservas_cache
from utils.formatters import criar_mapa_veiculos, criar_mapa_motoristas, exibir_reserva_no_calendario
from pages.components.components import renderizar_filtros_reservas
from pages.styles import CALENDAR_CSS
from config.settings import CALENDAR_OPTIONS


def renderizar():
    """Renderiza a tela de reservas."""
    st.title("Calendário de Reservas")
    
    # Busca dados
    dados_reservas = fetch_reservas()
    dados_veiculos = fetch_veiculos()
    dados_motoristas = fetch_motoristas()
    
    mapa_veiculos = criar_mapa_veiculos(dados_veiculos)
    mapa_motoristas = criar_mapa_motoristas(dados_motoristas)
    mapa_cores = {v["id"]: v.get("Cor", "#FF4B4B") for v in dados_veiculos}

    # Renderiza filtros reutilizáveis (calendário usa 1 data)
    filtro_data, filtro_veic, filtro_mot = renderizar_filtros_reservas(
        mapa_veiculos, mapa_motoristas, modo="calendario"
    )

    # Legenda dos veículos:
    st.markdown("### Legenda dos Veículos:")
    for veiculos in dados_veiculos:
        st.markdown(f"<div style='background-color: {veiculos['Cor']}; padding: 5px; margin: 5px; border-radius: 5px; color: white;'>{veiculos['Modelo']} - {veiculos['Referencia']}</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Configuração do calendário
    opcoes_calendario = CALENDAR_OPTIONS.copy()
    opcoes_calendario["initialDate"] = str(filtro_data)
    
    # Filtra e formata eventos
    eventos = exibir_reserva_no_calendario(
        dados_reservas,
        mapa_veiculos,
        mapa_motoristas,
        filtro_veic,
        filtro_mot,
        filtro_data_inicio=None,
        filtro_data_fim=None,
        mapa_cores=mapa_cores,
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
