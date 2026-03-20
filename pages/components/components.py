"""
Componentes reutilizáveis da interface.
"""
import streamlit as st
from utils.date_utils import para_formato_br


@st.dialog("Detalhes da Reserva")
def mostrar_detalhes(evento_info):
    """Exibe os detalhes de uma reserva em um diálogo."""
    reserva = evento_info.get('event', {})
    extended = reserva.get('extendedProps', {})
    reserva_id = reserva.get('id')
    
    # Formatar datas
    start_formatted = para_formato_br(reserva.get('start', ''))
    end_formatted = para_formato_br(reserva.get('end', ''))
    
    st.write(f"**Motivo:** {reserva.get('title', 'Sem título').replace('🚗 ', '')}")
    st.write(f"**Destino:** {extended.get('destino', 'Não informado')}")
    st.write(f"**Início:** {start_formatted}")
    st.write(f"**Fim:** {end_formatted}")
    st.write(f"**Veículo:** {extended.get('veiculo_nome', 'Não informado')}")
    st.write(f"**Motorista:** {extended.get('motorista_nome', 'Não informado')}")
    st.write(f"**Status:** {extended.get('status', 'Desconecido')}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state["reserva_em_edicao"] = reserva_id
            st.session_state["pagina"] = "editar_reserva"
            st.rerun()
            
    with col2:
        with st.popover("🗑️ Cancelar", use_container_width=True):
            st.markdown("⚠️ **Tem certeza?**")
            st.write("Esta ação não pode ser desfeita.")
            
            if st.button("Sim, excluir", type="primary", use_container_width=True):
                from database.supabase import delete_reserva, sincronizar_status_veiculo, clear_reservas_cache
                
                delete_reserva(reserva_id)
                
                veiculo_id = extended.get('veiculo_id')
                clear_reservas_cache()
                if veiculo_id:
                    sincronizar_status_veiculo(veiculo_id)
                
                
                st.rerun()


def renderizar_filtros_reservas(mapa_veiculos, mapa_motoristas, modo="calendario"):
    """Renderiza os filtros usados na lista e no calendário de reservas.

    Args:
        mapa_veiculos: dicionário id->nome de veículo
        mapa_motoristas: dicionário id->nome de motorista
        modo: "calendario" para filtro de data única, "lista" para intervalo de datas.

    Retorna:
        tuple:
            - Se modo == "calendario": (filtro_data, filtro_veiculo, filtro_motorista)
            - Se modo == "lista": (filtro_data_inicio, filtro_data_fim, filtro_veiculo, filtro_motorista)
    """
    if modo not in ("calendario", "lista"):
        raise ValueError("modo deve ser 'calendario' ou 'lista'")

    # Inicializa estado
    from utils.date_utils import hoje

    if modo == "calendario":
        if "filtro_data" not in st.session_state:
            st.session_state["filtro_data"] = hoje()
    else:
        if "filtro_data_inicio" not in st.session_state:
            st.session_state["filtro_data_inicio"] = hoje()
        if "filtro_data_fim" not in st.session_state:
            st.session_state["filtro_data_fim"] = hoje()

    if "filtro_veic" not in st.session_state:
        st.session_state["filtro_veic"] = "Todos"
    if "filtro_mot" not in st.session_state:
        st.session_state["filtro_mot"] = "Todos"

    def limpar_filtros():
        if modo == "calendario":
            st.session_state["filtro_data"] = hoje()
        else:
            st.session_state["filtro_data_inicio"] = hoje()
            st.session_state["filtro_data_fim"] = hoje()

        st.session_state["filtro_veic"] = "Todos"
        st.session_state["filtro_mot"] = "Todos"

    with st.expander("🔍 Buscar e Filtrar", expanded=True):
        if modo == "calendario":
            col_data, col_veic, col_mot, col_btn = st.columns([2, 2, 2, 1])

            with col_data:
                st.date_input("Ir para a data:", format="DD/MM/YYYY", key="filtro_data")
        else:
            col_data_inicio, col_data_fim, col_veic, col_mot, col_btn = st.columns([2, 2, 2, 2, 1])

            with col_data_inicio:
                st.date_input("Data início", format="DD/MM/YYYY", key="filtro_data_inicio")

            with col_data_fim:
                st.date_input("Data fim", format="DD/MM/YYYY", key="filtro_data_fim")

        with col_veic:
            st.selectbox(
                "Veículo",
                options=["Todos"] + list(mapa_veiculos.keys()),
                format_func=lambda x: "Todos" if x == "Todos" else mapa_veiculos[x],
                key="filtro_veic"
            )

        with col_mot:
            st.selectbox(
                "Motorista",
                options=["Todos"] + list(mapa_motoristas.keys()),
                format_func=lambda x: "Todos" if x == "Todos" else mapa_motoristas[x],
                key="filtro_mot"
            )

        with col_btn:
            st.write("")
            st.write("")
            st.button("🔄 Resetar", on_click=limpar_filtros, use_container_width=True)

    if modo == "calendario":
        return (
            st.session_state["filtro_data"],
            st.session_state["filtro_veic"],
            st.session_state["filtro_mot"],
        )

    return (
        st.session_state["filtro_data_inicio"],
        st.session_state["filtro_data_fim"],
        st.session_state["filtro_veic"],
        st.session_state["filtro_mot"],
    )


def exibir_foto_motorista(foto_url):
    """Exibe a foto de um motorista com estilo."""
    st.markdown(f'''
        <img src="{foto_url}" 
             style="width: 150px; height: 150px; object-fit: cover; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    ''', unsafe_allow_html=True)

