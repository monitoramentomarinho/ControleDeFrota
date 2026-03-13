"""
Tela de Veículos.
"""
import streamlit as st
import datetime
from database.supabase import fetch_veiculos, fetch_reservas
from utils.formatters import criar_mapa_veiculos
from utils.date_utils import agora_iso, de_iso, para_data_br


def renderizar():
    """Renderiza a tela de veículos."""
    st.title("Veículos PMAP")
    
    dados_veiculos = fetch_veiculos()
    dados_reservas = fetch_reservas()
    
    for veiculo in dados_veiculos:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1], gap="medium")
            
            with col1:
                st.image(veiculo.get("Icone", "https://via.placeholder.com/150"))
            
            with col2:
                st.subheader(veiculo["Modelo"])
                st.write(f"Placa: {veiculo['Placa']}")
                st.write(f"Status: {veiculo['Status']}")
                st.write(f"Referência: {veiculo['Referencia']}")
            
            with col3:
                hoje_iso = agora_iso()
                
                if veiculo["Status"] == "Disponível":
                    st.success("Disponível para reserva")
                elif veiculo["Status"] == "Reservado":
                    st.warning("Reservado")
                    reservas_do_veiculo = [
                        r for r in dados_reservas
                        if r["Veiculo_id"] == veiculo["id"]
                    ]
                    if reservas_do_veiculo:
                        st.write("Reservas:")
                        for r in reservas_do_veiculo:
                            data_inicio = para_data_br(r['data_retirada'])
                            data_fim = para_data_br(r['data_devolucao'])
                            st.write(f"- {data_inicio} a {data_fim}: {r['motivo_locacao']}")
                    else:
                        st.write("Nenhuma reserva encontrada.")
                elif veiculo["Status"] == "Manutenção":
                    st.error("Em manutenção")
