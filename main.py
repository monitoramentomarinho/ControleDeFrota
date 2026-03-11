"""
ControleDeFrota - Sistema de Gerenciamento de Reservas de Veículos (PMAP)

Aplicação principal que coordena todas as telas e a navegação.
"""
import streamlit as st
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT

# Configuração da página
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout=APP_LAYOUT)

# Inicializa estado da aplicação
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "home"



def main():
    """Função principal que renderiza a página atual."""
    # Importa as screens
    from ui.screens import home, reservas, veiculos, motoristas, cadastro_reserva, editar_reserva
    
    # Mapeia página para função de renderização
    screens = {
        "home": home.renderizar,
        "reservas": reservas.renderizar,
        "veiculos": veiculos.renderizar,
        "motoristas": motoristas.renderizar,
        "cadastro_reserva": cadastro_reserva.renderizar,
        "editar_reserva": editar_reserva.renderizar,
    }
    
    # Renderiza a tela atual
    pagina_atual = st.session_state.get("pagina", "home")
    if pagina_atual in screens:
        screens[pagina_atual]()
    else:
        st.error("Página não encontrada.")


def renderizar_sidebar():
    """Renderiza o menu da barra lateral."""
    with st.sidebar:
        st.subheader("Menu")
        
        if st.button("Início", icon="🏠", use_container_width=True):
            st.session_state["pagina"] = "home"
            st.rerun()
        
        if st.button("Calendário de Reservas", icon="🗓️", use_container_width=True):
            st.session_state["pagina"] = "reservas"
            st.rerun()
        
        if st.button("Veículos", icon="🛻", use_container_width=True):
            st.session_state["pagina"] = "veiculos"
            st.rerun()
        
        if st.button("Motoristas", icon="👥", use_container_width=True):
            st.session_state["pagina"] = "motoristas"
            st.rerun()


if __name__ == "__main__":
    renderizar_sidebar()
    main()





