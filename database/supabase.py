"""
Módulo de operações com Supabase.
Centraliza todas as interações com o banco de dados.
"""
import streamlit as st
import supabase as sb
from config.settings import (
    TABLE_RESERVAS,
    TABLE_VEICULOS,
    TABLE_MOTORISTAS,
    STORAGE_BUCKET,
    CACHE_TTL_RESERVAS,
    CACHE_TTL_VEICULOS,
    CACHE_TTL_MOTORISTAS,
)


@st.cache_resource
def get_supabase_client():
    """Retorna o cliente Supabase (inicializado apenas uma vez)."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return sb.create_client(url, key)


# ============= RESERVAS =============
@st.cache_data(ttl=CACHE_TTL_RESERVAS)
def fetch_reservas():
    """Busca todas as reservas do banco."""
    client = get_supabase_client()
    return client.table(TABLE_RESERVAS).select("*").execute().data


def insert_reserva(reserva_data):
    """Insere uma nova reserva no banco."""
    client = get_supabase_client()
    return client.table(TABLE_RESERVAS).insert(reserva_data).execute()


def update_reserva(reserva_id, reserva_data):
    """Atualiza uma reserva existente."""
    client = get_supabase_client()
    return client.table(TABLE_RESERVAS).update(reserva_data).eq("id", reserva_id).execute()


def delete_reserva(reserva_id):
    """Deleta uma reserva."""
    client = get_supabase_client()
    return client.table(TABLE_RESERVAS).delete().eq("id", reserva_id).execute()


def clear_reservas_cache():
    """Limpa o cache de reservas."""
    fetch_reservas.clear()


# ============= VEÍCULOS =============
@st.cache_data(ttl=CACHE_TTL_VEICULOS)
def fetch_veiculos():
    """Busca todos os veículos do banco."""
    client = get_supabase_client()
    return client.table(TABLE_VEICULOS).select("*").execute().data


def update_veiculo_status(veiculo_id, novo_status):
    """Atualiza o status de um veículo."""
    client = get_supabase_client()
    return client.table(TABLE_VEICULOS).update({"Status": novo_status}).eq("id", veiculo_id).execute()


def clear_veiculos_cache():
    """Limpa o cache de veículos."""
    fetch_veiculos.clear()


# ============= MOTORISTAS =============
@st.cache_data(ttl=CACHE_TTL_MOTORISTAS)
def fetch_motoristas():
    """Busca todos os motoristas do banco."""
    client = get_supabase_client()
    return client.table(TABLE_MOTORISTAS).select("*").execute().data


def insert_motorista(motorista_data):
    """Insere um novo motorista no banco."""
    client = get_supabase_client()
    return client.table(TABLE_MOTORISTAS).insert(motorista_data).execute()


def clear_motoristas_cache():
    """Limpa o cache de motoristas."""
    fetch_motoristas.clear()


# ============= STORAGE (IMAGENS) =============
def upload_imagem(caminho_armazenamento, bytes_arquivo, content_type):
    """
    Faz upload de uma imagem para o storage.
    
    Args:
        caminho_armazenamento: Caminho dentro do bucket (ex: "motoristas/foto.jpg")
        bytes_arquivo: Bytes do arquivo
        content_type: Tipo MIME do arquivo
    
    Returns:
        URL pública da imagem
    """
    client = get_supabase_client()
    client.storage.from_(STORAGE_BUCKET).upload(
        path=caminho_armazenamento,
        file=bytes_arquivo,
        file_options={"content-type": content_type}
    )
    
    url_response = client.storage.from_(STORAGE_BUCKET).get_public_url(caminho_armazenamento)
    
    if isinstance(url_response, dict):
        return url_response.get("public_url", url_response)
    elif hasattr(url_response, 'public_url'):
        return url_response.public_url
    
    return url_response


# ============= UTILITÁRIOS =============
def sincronizar_status_veiculo(veiculo_id, reservas=None):
    """
    Sincroniza o status de um veículo baseado em suas reservas ativas.
    
    Args:
        veiculo_id: ID do veículo
        reservas: Lista de reservas (se None, busca do banco)
    """
    import datetime
    from utils.date_utils import agora_iso
    
    # Busca o status atual
    client = get_supabase_client()
    veiculo = client.table(TABLE_VEICULOS).select("Status").eq("id", veiculo_id).execute().data
    
    if not veiculo or veiculo[0].get("Status") == "Manutenção":
        return
    
    # Se não receber as reservas, busca do banco
    if reservas is None:
        reservas = fetch_reservas()
    
    # Verifica se há reservas ativas/futuras
    reservas_ativas = [
        r for r in reservas
        if r["Veiculo_id"] == veiculo_id and r["data_devolucao"] >= agora_iso()
    ]
    
    novo_status = "Reservado" if len(reservas_ativas) > 0 else "Disponível"
    
    # Atualiza apenas se necessário
    if veiculo[0].get("Status") != novo_status:
        update_veiculo_status(veiculo_id, novo_status)
        clear_veiculos_cache()
