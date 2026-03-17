"""
ControleDeFrota - Sistema de Gerenciamento de Reservas de Veículos (PMAP)
Aplicação principal usando a navegação nativa do Streamlit (st.navigation)
"""
import streamlit as st
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT

# 1. Configuração da página sempre vem primeiro
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="collapsed" 
)

# 2. Importa as suas telas que já estão prontas
from pages.screens import devolucao, home, reservas, veiculos, motoristas, cadastro_reserva, devolucao

# 3. Transforma as suas funções em Páginas Nativas do Streamlit
# O parâmetro url_path garante que cada tela tenha seu próprio link único (ex: /home, /veiculos)
pg_home = st.Page(home.renderizar, title="Início", icon="🏠", default=True, url_path="home")
pg_reservas = st.Page(reservas.renderizar, title="Calendário de Reservas", icon="🗓️", url_path="reservas")
pg_veiculos = st.Page(veiculos.renderizar, title="Veículos", icon="🛻", url_path="veiculos")
pg_motoristas = st.Page(motoristas.renderizar, title="Motoristas", icon="👥", url_path="motoristas")

# Agrupando telas de formulário em uma seção separada
pg_cad_reserva = st.Page(cadastro_reserva.renderizar, title="Cadastrar Nova Reserva", icon="➕", url_path="cadastrar_reserva")
pg_devolucao = st.Page(devolucao.renderizar, title="Registrar Devolução", icon="✅", url_path="devolucao")

# 4. Configura o menu e as seções
menu = {
    "Menu Principal": [pg_home, pg_reservas, pg_veiculos, pg_motoristas],
    "Ações e Lançamentos": [pg_cad_reserva, pg_devolucao]
}

# 5. Roda a navegação mágica do Streamlit
nav = st.navigation(menu)
nav.run()