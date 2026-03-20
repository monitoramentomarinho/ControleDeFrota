import streamlit as st
import datetime
import io
from PIL import Image

from database.supabase import (
    fetch_veiculos, 
    fetch_motoristas, 
    fetch_reservas, 
    upload_imagem, 
    update_reserva, # AVISO: Importamos update_reserva em vez de delete_reserva!
    listar_fotos_devolucao,
    clear_reservas_cache, 
    clear_veiculos_cache,
    sincronizar_status_veiculo
)
from utils.formatters import criar_mapa_veiculos, criar_mapa_motoristas

def comprimir_imagem(imagem_bytes, qualidade=60):
    img = Image.open(io.BytesIO(imagem_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=qualidade)
    return output.getvalue()

def renderizar():
    st.title("Devolução de Veículos")
    st.write("Aqui você pode registrar a devolução dos veículos reservados.")

    reservas = fetch_reservas()
    dados_veiculos = fetch_veiculos()
    dados_motoristas = fetch_motoristas()

    mapa_veiculos = criar_mapa_veiculos(dados_veiculos)
    mapa_motoristas = criar_mapa_motoristas(dados_motoristas)

    if "reserva_devolucao" not in st.session_state:
        st.session_state.reserva_devolucao = None
    
    if "ver_fotos_reserva" not in st.session_state:
        st.session_state.ver_fotos_reserva = None
    
    # ===== MODO DE VISUALIZAÇÃO DE FOTOS =====
    if st.session_state.ver_fotos_reserva is not None:
        reserva_fotos = st.session_state.ver_fotos_reserva
        st.subheader(f"Fotos da Devolução - {reserva_fotos['motivo_locacao']}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Veículo:** {mapa_veiculos.get(reserva_fotos['Veiculo_id'], 'Desconhecido')}")
            st.write(f"**Motorista:** {mapa_motoristas.get(reserva_fotos['id_motorista'], 'Desconhecido')}")
            st.write(f"**Combustível Restante:** {reserva_fotos.get('combustivel_restante', 'N/A')}")
        with col2:
            if st.button("Voltar", use_container_width=True):
                st.session_state.ver_fotos_reserva = None
                st.rerun()
        
        st.divider()
        
        # Busca as fotos da devolução
        fotos = listar_fotos_devolucao(reserva_fotos['id'])
        
        if not fotos:
            st.warning("Nenhuma foto encontrada para esta devolução.")
        else:
            st.write(f"**Total de fotos:** {len(fotos)}")
            
            # Exibe as fotos em um grid
            cols = st.columns(2)
            for idx, foto in enumerate(fotos):
                with cols[idx % 2]:
                    st.image(foto['url'], caption=foto['nome'], use_container_width=True)
        
        return  # Sai da função, não executa o resto do código
    
    if st.session_state.reserva_devolucao is None:
        # ===== MODO NORMAL - LISTA DE RESERVAS =====
        
        # --- SEPARA AS RESERVAS EM DUAS LISTAS ---
        reservas_em_andamento = [r for r in reservas if r.get("status") != "Concluida"]
        
        # Pega as concluidas, ordena pelas mais recentes e pega as 5 primeiras
        reservas_concluidas = [r for r in reservas if r.get("status") == "Concluida"]
        reservas_concluidas.sort(key=lambda x: x.get("data_devolucao", ""), reverse=True)
        ultimas_cinco = reservas_concluidas[:5]

        # --- SEÇÃO 1: PARA DEVOLVER ---
        st.subheader("Reservas em Andamento")
        if not reservas_em_andamento:
            st.info("Nenhuma reserva aguardando devolução no momento.")
            
        for reserva in reservas_em_andamento:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    destino_txt = f" - {reserva.get('destino')}" if reserva.get('destino') else ""
                    st.write(f"**{reserva['motivo_locacao']}**{destino_txt}")
                    st.write(f"Veículo: {mapa_veiculos.get(reserva['Veiculo_id'], 'Desconhecido')} | Motorista: {mapa_motoristas.get(reserva['id_motorista'], 'Desconhecido')}")
                with col2:
                    if st.button(type="primary", label="Devolver", key=f"devolver_{reserva['id']}", use_container_width=True):
                        st.session_state.reserva_devolucao = reserva
                        st.rerun()
        
        st.divider()
        
        # --- SEÇÃO 2: HISTÓRICO ---
        st.subheader("Últimas 5 Devoluções")
        if not ultimas_cinco:
            st.write("Nenhuma devolução concluída ainda.")
            
        for concluida in ultimas_cinco:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    destino_txt = f" - {concluida.get('destino')}" if concluida.get('destino') else ""
                    st.write(f"**{concluida['motivo_locacao']}**{destino_txt}")
                    st.write(f"Veículo: {mapa_veiculos.get(concluida['Veiculo_id'], 'Desconhecido')} | Motorista: {mapa_motoristas.get(concluida['id_motorista'], 'Desconhecido')}")
                    st.write(f"Combustivel Restante: {concluida.get('combustivel_restante', 'N/A')}")
                with col2:
                    if st.button(label="Ver Fotos", key=f"fotos_{concluida['id']}", use_container_width=True):
                        st.session_state.ver_fotos_reserva = concluida
                        st.rerun()
    
    else:
        # --- MODO DE FORMULÁRIO DE DEVOLUÇÃO ---
        reserva_selecionada = st.session_state.reserva_devolucao
        st.subheader(f"Devolução - {reserva_selecionada['motivo_locacao']}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Veículo:** {mapa_veiculos.get(reserva_selecionada['Veiculo_id'], 'Desconhecido')}")
            st.write(f"**Motorista:** {mapa_motoristas.get(reserva_selecionada['id_motorista'], 'Desconhecido')}")
        with col2:
            if st.button("Voltar", use_container_width=True):
                st.session_state.reserva_devolucao = None
                st.rerun()
        
        with st.form("Formulário de Devolução", clear_on_submit=False):
            st.write("Preencha os dados da devolução:")
            nivel_combustivel = st.radio("Nível de Combustível:", options=["Cheio", "1/2", "1/4", "Reserva"])
            
            foto_t = st.file_uploader("Foto do Veículo (Traseira)", type=["jpg", "jpeg", "png"])
            foto_f = st.file_uploader("Foto do Veículo (Frontal)", type=["jpg", "jpeg", "png"])
            foto_ld = st.file_uploader("Foto do Veículo (Lateral Direita)", type=["jpg", "jpeg", "png"])
            foto_le = st.file_uploader("Foto do Veículo (Lateral Esquerda)", type=["jpg", "jpeg", "png"])

            if st.form_submit_button("Registrar Devolução", type="primary"):
                fotos_para_enviar = [
                    ("Traseira", foto_t), ("Frontal", foto_f), 
                    ("Lateral_Direita", foto_ld), ("Lateral_Esquerda", foto_le)
                ]
                
                fotos_validas = [(nome, f) for nome, f in fotos_para_enviar if f is not None]
                
                if len(fotos_validas) > 3:
                    with st.spinner("Registrando devolução e salvando fotos..."):
                        try:
                            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                            
                            for nome_foto, arquivo in fotos_validas:
                                bytes_comprimidos = comprimir_imagem(arquivo.getvalue())
                                caminho_storage = f"devolucoes/reserva_{reserva_selecionada['id']}_{nome_foto}_{timestamp}.jpg"
                                upload_imagem(caminho_storage, bytes_comprimidos, "image/jpeg")
                            
                            veiculo_id = reserva_selecionada['Veiculo_id']
                            
                            dados_atualizacao = {
                                "status": "Concluida",
                                "combustivel_restante": nivel_combustivel
                            }
                            update_reserva(reserva_selecionada['id'], dados_atualizacao)
                            
                            # Atualiza a memória
                            clear_reservas_cache()
                            clear_veiculos_cache()
                            
                            # Libera o veículo
                            sincronizar_status_veiculo(veiculo_id)
                            
                            st.success("Devolução registrada com sucesso!")
                            st.session_state.reserva_devolucao = None
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Erro ao processar devolução: {e}")
                else:
                    st.error("Por favor, envie todas as fotos para vistoria.")