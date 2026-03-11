"""
Funções utilitárias para manipulação de datas.
"""
import datetime
from config.settings import DATETIME_FORMAT, ISO_DATETIME_FORMAT


def agora_iso():
    """Retorna a data e hora atual em formato ISO."""
    return datetime.datetime.now().isoformat()


def agora():
    """Retorna a data e hora atual como datetime."""
    return datetime.datetime.now()


def para_iso(dt):
    """Converte um datetime para formato ISO."""
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


def de_iso(iso_str):
    """Converte uma string ISO para datetime."""
    if isinstance(iso_str, datetime.datetime):
        return iso_str
    try:
        return datetime.datetime.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return datetime.datetime.now()


def para_formato_br(iso_str):
    """Converte ISO para formato brasileiro (dd/mm/yyyy hh:mm)."""
    dt = de_iso(iso_str)
    return dt.strftime(DATETIME_FORMAT)


def para_data_br(iso_str):
    """Converte ISO para formato água brasileiro (dd/mm/yyyy)."""
    dt = de_iso(iso_str)
    return dt.strftime("%d/%m/%Y")


def hoje():
    """Retorna a data de hoje."""
    return datetime.date.today()


def tem_sobreposicao(inicio1, fim1, inicio2, fim2):
    """
    Verifica se dois períodos de tempo se sobrepõem.
    
    Args:
        inicio1, fim1: Datetime do primeiro período
        inicio2, fim2: Datetime do segundo período
    
    Returns:
        True se há sobreposição, False caso contrário
    """
    return (inicio1 < fim2) and (fim1 > inicio2)
