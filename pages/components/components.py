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
    st.write(f"**Início:** {start_formatted}")
    st.write(f"**Fim:** {end_formatted}")
    st.write(f"**Veículo:** {extended.get('veiculo_nome', 'Não informado')}")
    st.write(f"**Motorista:** {extended.get('motorista_nome', 'Não informado')}")
    
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


def exibir_foto_motorista(foto_url):
    """Exibe a foto de um motorista com estilo."""
    st.markdown(f'''
        <img src="{foto_url}" 
             style="width: 150px; height: 150px; object-fit: cover; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    ''', unsafe_allow_html=True)

