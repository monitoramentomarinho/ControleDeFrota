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


def listar_fotos_devolucao(reserva_id):
    """
    Lista todas as fotos de uma devolução específica.
    
    Args:
        reserva_id: ID da reserva
    
    Returns:
        Lista de dicionários com {'nome': str, 'url': str} para cada foto
    """
    client = get_supabase_client()
    try:
        # Lista todos os arquivos que começam com "devolucoes/" e contêm o reserva_id
        lista_completa = client.storage.from_(STORAGE_BUCKET).list("devolucoes")
        
        fotos = []
        
        # Recursivamente procura por fotos da reserva em todas as subpastas
        def procurar_fotos_recursivo(caminho, prefixo_procura):
            try:
                items = client.storage.from_(STORAGE_BUCKET).list(caminho)
                for item in items:
                    # Se for diretório, continua buscando
                    if item.get('name') and not item.get('id'):
                        novo_caminho = f"{caminho}/{item['name']}" if caminho else item['name']
                        procurar_fotos_recursivo(novo_caminho, prefixo_procura)
                    # Se for arquivo e contém o prefixo procurado
                    elif item.get('name') and prefixo_procura in item.get('name', ''):
                        caminho_completo = f"{caminho}/{item['name']}" if caminho else item['name']
                        url = client.storage.from_(STORAGE_BUCKET).get_public_url(caminho_completo)
                        if isinstance(url, dict):
                            url = url.get("public_url", url)
                        
                        fotos.append({
                            'nome': item['name'],
                            'url': url,
                            'caminho': caminho_completo
                        })
            except Exception:
                pass
        
        procurar_fotos_recursivo("devolucoes", f"reserva_{reserva_id}")
        return fotos
        
    except Exception as e:
        st.warning(f"Erro ao listar fotos: {e}")
        return []


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
        if r["Veiculo_id"] == veiculo_id 
        and r["data_devolucao"] >= agora_iso()
        and r.get("status", "Em andamento") == "Em andamento"
    ]
    
    novo_status = "Reservado" if len(reservas_ativas) > 0 else "Disponível"
    
    # Atualiza apenas se necessário
    if veiculo[0].get("Status") != novo_status:
        update_veiculo_status(veiculo_id, novo_status)
        clear_veiculos_cache()
