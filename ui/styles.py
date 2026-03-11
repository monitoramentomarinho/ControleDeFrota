"""
Estilos CSS da aplicação.
"""

CALENDAR_CSS = """
    /* ========================================
    1. ESTILO DOS BLOCOS DE RESERVA (EVENTOS)
    ======================================== */
    .fc-event {
        border-radius: 6px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
        padding: 2px;
        transition: transform 0.2s ease; /* Animação suave */
    }
    
    /* Efeito de flutuar ao passar o mouse (Apenas PC) */
    .fc-event:hover {
        transform: scale(1.02);
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }

    /* Texto dentro da reserva mais legível */
    .fc-event-title {
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    
    .fc-event-time {
        font-size: 0.75rem !important;
        opacity: 0.9;
    }

    /* ========================================
    2. BOTÕES DE NAVEGAÇÃO DO TOPO
    ======================================== */
    .fc .fc-button-primary {
        background-color: transparent !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        text-transform: capitalize;
        font-weight: bold;
        transition: all 0.2s;
    }
    
    /* Cor do botão quando clicado ou com mouse em cima */
    .fc .fc-button-primary:not(:disabled).fc-button-active, 
    .fc .fc-button-primary:not(:disabled):active, 
    .fc .fc-button-primary:hover {
        background-color: #fdcd2d !important;
        color: white !important;
    }

    /* Fundo sutil para destacar a coluna do dia de HOJE */
    .fc-day-today {
        background-color: rgba(255, 75, 75, 0.04) !important;
    }

    /* ========================================
    3. RESPONSIVIDADE (MAGIA PARA O CELULAR)
    ======================================== */
    @media (max-width: 768px) {
        /* Empilha os botões do cabeçalho para não vazar da tela */
        .fc-header-toolbar {
            flex-direction: column !important;
            gap: 12px !important;
        }
        
        /* Ajusta o tamanho do título (Ex: "Outubro 2023") */
        .fc-toolbar-title {
            font-size: 1.3rem !important;
            text-align: center;
        }
        
        /* Encolhe um pouco os botões para caberem lado a lado */
        .fc-button {
            padding: 0.4em 0.6em !important;
            font-size: 0.85rem !important;
        }
        
        /* Ajusta o texto dos dias na grade (se o usuário usar a visão de semana no celular) */
        .fc-col-header-cell-cushion {
            font-size: 0.8rem !important;
        }
        
        /* Ajustes específicos para a visão de "Agenda" (listWeek) no celular */
        .fc-list-event-title {
            font-size: 0.9rem !important;
            font-weight: bold !important;
        }
        .fc-list-event-time {
            font-size: 0.85rem !important;
            color: #555 !important;
        }
    }
"""
