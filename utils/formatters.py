"""
Funções de formatação de dados.
"""
import ast
from utils.date_utils import para_data_br


def extrair_numero_telefone(telefone_raw):
    """Extrai o número de telefone, tratando o caso onde ele vem como dicionário do widget.

    Args:
        telefone_raw: String ou dict com dados do telefone

    Returns:
        String com o número de telefone limpo (apenas dígitos)
    """
    if isinstance(telefone_raw, dict):
        return telefone_raw.get("number", "")

    telefone_str = str(telefone_raw)

    # Se começar com {'type':", tenta desempacotar
    if "{'type':" in telefone_str:
        try:
            tel_dict = ast.literal_eval(telefone_str)
            return tel_dict.get('number', telefone_str)
        except:
            pass

    # Mantém apenas dígitos (remove formatação)
    return "".join([c for c in telefone_str if c.isdigit()])


def formatar_telefone_br(telefone):
    """Formata um telefone brasileiro (somente dígitos) para a máscara (XX) XXXXX-XXXX."""
    if not telefone:
        return ""

    digitos = "".join([c for c in str(telefone) if c.isdigit()])
    if len(digitos) == 11:  # (XX) 9XXXX-XXXX
        return f"({digitos[0:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:  # (XX) XXXX-XXXX
        return f"({digitos[0:2]}) {digitos[2:6]}-{digitos[6:]}"
    # fallback genérico
    return digitos


def formatar_veiculo(veiculo):
    """Formata dados de um veículo para exibição."""
    return f"{veiculo['Modelo']} ({veiculo['Referencia']})"


def formatar_veiculo_com_placa(veiculo):
    """Formata dados de um veículo com placa."""
    return f"{veiculo['Modelo']} ({veiculo['Placa']})"


def criar_mapa_veiculos(veiculos):
    """Cria um dicionário ID -> Nome do veículo."""
    return {v["id"]: formatar_veiculo(v) for v in veiculos}


def criar_mapa_motoristas(motoristas):
    """Cria um dicionário ID -> Nome do motorista."""
    return {m["id"]: m["Nome"] for m in motoristas}


def formatar_reserva_para_calendario(reserva, mapa_veiculos, mapa_motoristas, mapa_cores=None):
    """Formata uma reserva para ser exibida no calendário de forma segura."""
    
    # Tratamento de segurança para evitar falhas silenciosas do FullCalendar
    motivo = reserva.get("motivo_locacao") or "Sem motivo"
    
    cor_evento = "#FF4B4B"
    if mapa_cores and reserva["Veiculo_id"] in mapa_cores:
        cor_evento = mapa_cores[reserva["Veiculo_id"]]
    
    return {
        "id": str(reserva.get("id", "")), # Força ser string
        "title": f"{motivo} - {mapa_motoristas.get(reserva.get('id_motorista'), 'N/A')}",
        "start": reserva.get("data_retirada"),
        "end": reserva.get("data_devolucao"),
        "backgroundColor": cor_evento,
        "borderColor": cor_evento,
        "textColor": "#FFFFFF",
        "extendedProps": {
            "motorista": mapa_motoristas.get(reserva.get("id_motorista"), "N/A"),
            "veiculo_nome": mapa_veiculos.get(reserva.get("Veiculo_id"), "Desconhecido"),
            "veiculo_id": reserva.get("Veiculo_id"),
            "motorista_nome": mapa_motoristas.get(reserva.get("id_motorista"), "Desconhecido"),
            "destino": reserva.get("motivo_locacao", "Não informado"),
            "status": reserva.get("status", "Desconhecido")
        }
    }


from utils.date_utils import de_iso


def filtrar_reservas(
    reservas,
    filtro_veiculo="Todos",
    filtro_motorista="Todos",
    filtro_data_inicio=None,
    filtro_data_fim=None,
):
    """Filtra reservas por veículo, motorista e intervalo de datas."""
    eventos = []

    for reserva in reservas:
        if filtro_veiculo != "Todos" and reserva["Veiculo_id"] != filtro_veiculo:
            continue

        if filtro_motorista != "Todos" and reserva.get("id_motorista") != filtro_motorista:
            continue

        # Filtro de data (interseção de intervalo)
        if filtro_data_inicio and filtro_data_fim:
            inicio_reserva = de_iso(reserva.get("data_retirada"))
            fim_reserva = de_iso(reserva.get("data_devolucao"))

            if fim_reserva.date() < filtro_data_inicio or inicio_reserva.date() > filtro_data_fim:
                continue

        eventos.append(reserva)

    return eventos


def exibir_reserva_no_calendario(
    reservas,
    mapa_veiculos,
    mapa_motoristas,
    filtro_veiculo="Todos",
    filtro_motorista="Todos",
    filtro_data_inicio=None,
    filtro_data_fim=None,
    mapa_cores=None,
):
    """Filtra e formata reservas para o calendário."""
    reservas_filtradas = filtrar_reservas(
        reservas,
        filtro_veiculo,
        filtro_motorista,
        filtro_data_inicio,
        filtro_data_fim,
    )
    return [
        formatar_reserva_para_calendario(r, mapa_veiculos, mapa_motoristas, mapa_cores)
        for r in reservas_filtradas
    ]
