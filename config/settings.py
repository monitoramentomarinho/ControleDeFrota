"""
Configurações e constantes da aplicação.
"""
import datetime

# ============= CONFIGURAÇÕES STREAMLIT =============
APP_TITLE = "PMAP - Reservas de Veículos"
APP_ICON = "🚗"
APP_LAYOUT = "wide"

# ============= CONSTANTES DE STATUS =============
STATUS_DISPONIVEL = "Disponível"
STATUS_RESERVADO = "Reservado"
STATUS_MANUTENCAO = "Manutenção"

STATUS_VALUES = [STATUS_DISPONIVEL, STATUS_RESERVADO, STATUS_MANUTENCAO]

# ============= CONFIGURAÇÕES DE CACHE =============
CACHE_TTL_RESERVAS = 60  # segundos
CACHE_TTL_VEICULOS = 60  # segundos
CACHE_TTL_MOTORISTAS = 60  # segundos

# ============= CONFIGURAÇÕES DO CALENDÁRIO =============
CALENDAR_OPTIONS = {
    "locale": "pt-br",
    "headerToolbar": {
        "left": "prev,next",
        "center": "title",
        "right": "today dayGridMonth,timeGridDay,listWeek",
    },
    "initialView": "dayGridMonth",
    "slotMinTime": "06:00:00",
    "slotMaxTime": "22:00:00",
    "allDaySlot": False,
    "height": "auto",
    "buttonText": {
        "today": "Hoje",
        "day": "Dia",
        "list": "Agenda"
    }
}

# ============= CORES =============
COLOR_RESERVATION = "#FF4B4B"
COLOR_PRIMARY = "#fdcd2d"

# ============= TABELAS SUPABASE =============
TABLE_RESERVAS = "Reservas"
TABLE_VEICULOS = "CadastroVeiculos"
TABLE_MOTORISTAS = "Motoristas"

# ============= CAMPOS DA REATIVAR =============
RESERVA_FIELDS = {
    "id": "id",
    "motivo": "motivo_locacao",
    "data_retirada": "data_retirada",
    "data_devolucao": "data_devolucao",
    "veiculo_id": "Veiculo_id",
    "motorista_id": "id_motorista",
}

# ============= CAMPOS DO VEÍCULO =============
VEICULO_FIELDS = {
    "id": "id",
    "modelo": "Modelo",
    "placa": "Placa",
    "status": "Status",
    "referencia": "Referencia",
    "icone": "Icone",
}

# ============= CAMPOS DO MOTORISTA =============
MOTORISTA_FIELDS = {
    "id": "id",
    "nome": "Nome",
    "telefone": "Telefone",
    "foto": "Foto_perfil",
}

# ============= ARMAZENAMENTO DE IMAGENS =============
STORAGE_BUCKET = "Imagens"
STORAGE_MOTORISTAS_PATH = "motoristas"

# ============= FORMATO DE DATA =============
DATE_FORMAT = "DD/MM/YYYY"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"
ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
