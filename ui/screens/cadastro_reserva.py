"""
Tela de Cadastro de Reserva.
"""
import streamlit as st
from database.supabase import (
    fetch_reservas,
    fetch_veiculos,
    fetch_motoristas,
    insert_reserva,
    sincronizar_status_veiculo,
    clear_reservas_cache,
)
from utils.formatters import criar_mapa_veiculos, criar_mapa_motoristas
from utils.date_utils import tem_sobreposicao


def renderizar():
    """Renderiza a tela de cadastro de reserva."""
    st.title("Cadastrar Nova Reserva")
    
    lista_veiculos = fetch_veiculos()
    lista_motoristas = fetch_motoristas()
    lista_reservas = fetch_reservas()
    
    mapa_veiculos = criar_mapa_veiculos(lista_veiculos)
    mapa_motoristas = criar_mapa_motoristas(lista_motoristas)
    status_map = {v["id"]: v["Status"] for v in lista_veiculos}
    
    with st.form("Formulário de Reserva", clear_on_submit=True):
        motivo = st.text_input("Motivo da Locação")
        data_retirada = st.datetime_input("Data da Retirada", format="DD/MM/YYYY")
        data_devolucao = st.datetime_input("Data da Devolução", format="DD/MM/YYYY")
        
        veiculo_id = st.selectbox(
            "Selecione o Veículo",
            options=list(mapa_veiculos.keys()),
            format_func=lambda x: f"{mapa_veiculos[x]} - {status_map[x]}"
        )
        
        motorista_id = st.selectbox(
            "Selecione o Motorista",
            options=list(mapa_motoristas.keys()),
            format_func=lambda x: mapa_motoristas[x]
        )
        
        if st.form_submit_button("Salvar Reserva"):
            # Validação de datas
            if data_retirada >= data_devolucao:
                st.error("A data de retirada deve ser anterior à data de devolução.")
            else:
                # Verifica conflitos
                conflito = False
                for reserva in lista_reservas:
                    if reserva["Veiculo_id"] == veiculo_id:
                        existing_start = reserva["data_retirada"]
                        existing_end = reserva["data_devolucao"]
                        if tem_sobreposicao(data_retirada, data_devolucao, existing_start, existing_end):
                            conflito = True
                            break
                
                if conflito:
                    st.error("Já existe uma reserva para este veículo no período selecionado.")
                else:
                    # Insere nova reserva
                    nova_reserva = {
                        "motivo_locacao": motivo,
                        "data_retirada": data_retirada.isoformat(),
                        "data_devolucao": data_devolucao.isoformat(),
                        "Veiculo_id": veiculo_id,
                        "id_motorista": motorista_id
                    }
                    insert_reserva(nova_reserva)
                    sincronizar_status_veiculo(veiculo_id)
                    clear_reservas_cache()
                    
                    st.session_state["pagina"] = "reservas"
                    st.rerun()
