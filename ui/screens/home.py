"""
Tela inicial (Home).
"""
import streamlit as st
from database.supabase import fetch_reservas
from utils.date_utils import para_data_br


def renderizar():
    """Renderiza a tela inicial."""
    st.title("Bem-vindo ao PMAP!")
    st.write("Este é o sistema de gerenciamento de reservas de veículos da PMAP. Use o menu à esquerda para navegar.")
    
    st.subheader("Próximas Reservas:")
    
    reservas = fetch_reservas()
    if reservas:
        for reserva in reservas:
            data_inicio = para_data_br(reserva['data_retirada'])
            data_fim = para_data_br(reserva['data_devolucao'])
            st.write(f"- {reserva['motivo_locacao']} ({data_inicio} a {data_fim})")
    else:
        st.write("Nenhuma reserva futura encontrada.")
