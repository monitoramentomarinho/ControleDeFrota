"""
Tela de Edição de Reserva.
"""
import streamlit as st
from database.supabase import (
    fetch_reservas,
    fetch_veiculos,
    fetch_motoristas,
    update_reserva,
    sincronizar_status_veiculo,
    clear_reservas_cache,
)
from utils.formatters import criar_mapa_veiculos, criar_mapa_motoristas
from utils.date_utils import de_iso, tem_sobreposicao
import datetime


def renderizar():
    """Renderiza a tela de edição de reserva."""
    st.title("Editar Reserva")
    
    reserva_id = st.session_state.get("reserva_em_edicao")
    
    # Redireciona se não tiver ID
    if not reserva_id:
        st.session_state["pagina"] = "reservas"
        st.rerun()
    
    lista_reservas = fetch_reservas()
    lista_veiculos = fetch_veiculos()
    lista_motoristas = fetch_motoristas()
    
    # Busca a reserva atual
    reserva_atual = next((r for r in lista_reservas if str(r["id"]) == str(reserva_id)), None)
    
    if not reserva_atual:
        st.error("Reserva não encontrada no banco de dados.")
        st.stop()
    
    mapa_veiculos = criar_mapa_veiculos(lista_veiculos)
    mapa_motoristas = criar_mapa_motoristas(lista_motoristas)
    
    # Índices iniciais nos selects
    opcoes_veiculos = list(mapa_veiculos.keys())
    index_veiculo = opcoes_veiculos.index(reserva_atual["Veiculo_id"]) if reserva_atual["Veiculo_id"] in opcoes_veiculos else 0
    
    opcoes_motoristas = list(mapa_motoristas.keys())
    index_motorista = opcoes_motoristas.index(reserva_atual["id_motorista"]) if reserva_atual["id_motorista"] in opcoes_motoristas else 0
    
    # Converte datas
    try:
        inicio_default = de_iso(reserva_atual["data_retirada"])
        fim_default = de_iso(reserva_atual["data_devolucao"])
    except Exception:
        inicio_default = datetime.datetime.now()
        fim_default = datetime.datetime.now()
    
    # Formulário de edição
    with st.form("Formulário de Edição"):
        motivo = st.text_input("Motivo da Locação", value=reserva_atual["motivo_locacao"])
        data_retirada = st.datetime_input("Data da Retirada", value=inicio_default, format="DD/MM/YYYY")
        data_devolucao = st.datetime_input("Data da Devolução", value=fim_default, format="DD/MM/YYYY")
        
        veiculo_id = st.selectbox(
            "Selecione o Veículo",
            options=opcoes_veiculos,
            format_func=lambda x: mapa_veiculos[x],
            index=index_veiculo
        )
        
        motorista_id = st.selectbox(
            "Selecione o Motorista",
            options=opcoes_motoristas,
            format_func=lambda x: mapa_motoristas[x],
            index=index_motorista
        )
        
        if st.form_submit_button("Salvar Alterações"):
            if data_retirada >= data_devolucao:
                st.error("A data de retirada deve ser anterior à data de devolução.")
            else:
                # Verifica conflitos
                conflito = False
                for r in lista_reservas:
                    if str(r["id"]) != str(reserva_id) and r["Veiculo_id"] == veiculo_id:
                        if tem_sobreposicao(data_retirada, data_devolucao, r["data_retirada"], r["data_devolucao"]):
                            conflito = True
                            break
                
                if conflito:
                    st.error("Já existe uma reserva para este veículo no período selecionado.")
                else:
                    # Atualiza
                    dados_atualizados = {
                        "motivo_locacao": motivo,
                        "data_retirada": data_retirada.isoformat(),
                        "data_devolucao": data_devolucao.isoformat(),
                        "Veiculo_id": veiculo_id,
                        "id_motorista": motorista_id
                    }
                    update_reserva(reserva_id, dados_atualizados)
                    clear_reservas_cache()
                    sincronizar_status_veiculo(veiculo_id)
                    
                    # Se trocou veículo, sincroniza o anterior também
                    if veiculo_id != reserva_atual["Veiculo_id"]:
                        sincronizar_status_veiculo(reserva_atual["Veiculo_id"])
                    
                    
                    st.session_state["pagina"] = "reservas"
                    st.rerun()
    
    # Botão de voltar
    if st.button("Voltar sem salvar"):
        st.session_state["pagina"] = "reservas"
        st.rerun()
