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
    
    from database.supabase import fetch_veiculos, fetch_motoristas
    from utils.formatters import criar_mapa_veiculos, criar_mapa_motoristas, filtrar_reservas
    from pages.components.components import renderizar_filtros_reservas

    dados_veiculos = fetch_veiculos()
    dados_motoristas = fetch_motoristas()

    mapa_veiculos = criar_mapa_veiculos(dados_veiculos)
    mapa_motoristas = criar_mapa_motoristas(dados_motoristas)

    filtro_inicio, filtro_fim, filtro_veic, filtro_mot = renderizar_filtros_reservas(
        mapa_veiculos, mapa_motoristas, modo="lista"
    )

    reservas_filtradas = filtrar_reservas(reservas, filtro_veic, filtro_mot, filtro_inicio, filtro_fim)

    if reservas_filtradas:
        for reserva in reservas_filtradas:
            data_inicio = para_data_br(reserva['data_retirada'])
            data_fim = para_data_br(reserva['data_devolucao'])
            st.write(f"- {reserva['motivo_locacao']} ({data_inicio} a {data_fim})")
    else:
        st.write("Nenhuma reserva encontrada para os filtros selecionados.")

    