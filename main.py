import streamlit as st
import streamlit_calendar as st_cal
import supabase as sb
from streamlit_phone_number import st_phone_number
import datetime

st.set_page_config(page_title="PMAP - Reservas de Veículos", page_icon="🚗", layout="wide")

# 1. CACHE DA CONEXÃO: Cria o cliente apenas uma vez
@st.cache_resource
def iniciar_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return sb.create_client(url, key)

supabase = iniciar_supabase()

# 2. CACHE DE DADOS: Evita ir ao banco a cada clique (Expira a cada 60 segundos)
@st.cache_data(ttl=60)
def buscar_reservas():
    return supabase.table("Reservas").select("*").execute().data

@st.cache_data(ttl=60)
def buscar_veiculos():
    return supabase.table("CadastroVeiculos").select("*").execute().data

@st.cache_data(ttl=60)
def buscar_motoristas():
    return supabase.table("Motoristas").select("*").execute().data

# --- Fim das otimizações de Backend ---

def sincronizar_status_veiculo(veiculo_id):
    """Verifica as reservas de um veículo e atualiza seu status automaticamente."""
    # 1. Checa o status atual (para não alterar se o carro estiver na oficina, por exemplo)
    veiculo = supabase.table("CadastroVeiculos").select("Status").eq("id", veiculo_id).execute().data
    if not veiculo or veiculo[0].get("Status") == "Manutenção":
        return

    # 2. Busca se há reservas ATIVAS ou FUTURAS para este veículo
    hoje_iso = datetime.datetime.now().isoformat()
    reservas_ativas = supabase.table("Reservas").select("id") \
        .eq("Veiculo_id", veiculo_id) \
        .gte("data_devolucao", hoje_iso).execute().data

    # 3. Decide qual deve ser o status real dele
    novo_status = "Reservado" if len(reservas_ativas) > 0 else "Disponível"

    # 4. Atualiza o banco apenas se o status estiver desatualizado
    if veiculo[0].get("Status") != novo_status:
        supabase.table("CadastroVeiculos").update({"Status": novo_status}).eq("id", veiculo_id).execute()
        buscar_veiculos.clear() # Limpa a memória para a tela atualizar na hora

@st.dialog("Detalhes da Reserva")
def mostrar_detalhes(evento_info):
    reserva = evento_info.get('event', {})
    extended = reserva.get('extendedProps', {})
    reserva_id = reserva.get('id')
    
    # Formatar datas
    try:
        start_dt = datetime.datetime.fromisoformat(reserva.get('start'))
        start_formatted = start_dt.strftime("%d/%m/%Y %H:%M")
    except:
        start_formatted = reserva.get('start', 'Não informado')
    
    try:
        end_dt = datetime.datetime.fromisoformat(reserva.get('end'))
        end_formatted = end_dt.strftime("%d/%m/%Y %H:%M")
    except:
        end_formatted = reserva.get('end', 'Não informado')
    
    st.write(f"**Motivo:** {reserva.get('title', 'Sem título').replace('🚗 ', '')}")
    st.write(f"**Início:** {start_formatted}")
    st.write(f"**Fim:** {end_formatted}")
    st.write(f"**Veículo:** {extended.get('veiculo_nome', 'Não informado')}")
    st.write(f"**Motorista:** {extended.get('motorista_nome', 'Não informado')}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✏️ Editar", use_container_width=True):
            st.session_state["reserva_em_edicao"] = reserva_id
            st.session_state["pagina"] = "editar_reserva"
            st.rerun()
            
    with col2:
        # Usamos st.popover no lugar do botão direto
        with st.popover("🗑️ Cancelar", use_container_width=True):
            st.markdown("⚠️ **Tem certeza?**")
            st.write("Esta ação não pode ser desfeita.")
            
            # Botão real de exclusão dentro do balão
            if st.button("Sim, excluir", type="primary", use_container_width=True):
                supabase.table("Reservas").delete().eq("id", reserva_id).execute()
                
                veiculo_id = extended.get('veiculo_id')
                if veiculo_id:
                    sincronizar_status_veiculo(veiculo_id)
                
                buscar_reservas.clear()
                st.rerun()
    
    
    
opcoes_calendario = {
    "locale": "pt-br",
    "headerToolbar": {
        "left": "prev,next",
        "center": "title",
        "right": "today dayGridMonth,timeGridDay,listWeek", # Mudei aqui para focar em "Dia" e "Agenda" no mobile
    },
    "initialView": "dayGridMonth", # A visão 'Lista' (Agenda) é PERFEITA para celular!
    "slotMinTime": "06:00:00",
    "slotMaxTime": "22:00:00",
    "allDaySlot": False,
    "height": "auto", # 👈 ISSO É CRUCIAL NO CELULAR (Evita o calendário ficar espremido com barra de rolagem interna)
    "buttonText": {
        "today": "Hoje",
        "day": "Dia",
        "list": "Agenda"
    }
}

css_brabo = """
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
        color: #ffffff !important; /* Cor principal (Vermelho Streamlit) */
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



def carregarPagina():
    # Só exibe as boas-vindas na tela inicial
    if st.session_state.get("pagina", "home") == "home":
        st.title("Bem-vindo ao PMAP!")
        st.write("Este é o sistema de gerenciamento de reservas de veículos da PMAP. Use o menu à esquerda para navegar.")
    
    match st.session_state.get("pagina", "home"):
        case "reservas":
            st.title("Calendário de Reservas")
            
            # 1. Puxa os dados primeiro
            dados_reservas = buscar_reservas()
            dados_veiculos = buscar_veiculos()
            dados_motoristas = buscar_motoristas()
            
            veiculo_map = {v["id"]: f"{v['Modelo']} ({v['Placa']})" for v in dados_veiculos}
            motorista_map = {m["id"]: m["Nome"] for m in dados_motoristas}
            
            opcoes_veic = ["Todos"] + list(veiculo_map.keys())
            opcoes_mot = ["Todos"] + list(motorista_map.keys())

            # 2. Inicializa os filtros na memória (se não existirem)
            if "filtro_data" not in st.session_state:
                st.session_state["filtro_data"] = datetime.date.today()
            if "filtro_veic" not in st.session_state:
                st.session_state["filtro_veic"] = "Todos"
            if "filtro_mot" not in st.session_state:
                st.session_state["filtro_mot"] = "Todos"

            # 3. Função que o botão vai chamar para limpar tudo
            def limpar_filtros():
                st.session_state["filtro_data"] = datetime.date.today()
                st.session_state["filtro_veic"] = "Todos"
                st.session_state["filtro_mot"] = "Todos"
            
            # 4. Área de Filtros
            with st.expander("🔍 Buscar e Filtrar", expanded=True):
                # Dividi em 4 colunas para o botão ficar do lado direito
                col_data, col_veic, col_mot, col_btn = st.columns([2, 2, 2, 1])
                
                with col_data:
                    # Note o uso do parâmetro "key" para vincular ao session_state
                    data_foco = st.date_input("Ir para a data:", format="DD/MM/YYYY", key="filtro_data")
                
                with col_veic:
                    filtro_veiculo = st.selectbox("Veículo", options=opcoes_veic, format_func=lambda x: "Todos" if x == "Todos" else veiculo_map[x], key="filtro_veic")
                    
                with col_mot:
                    filtro_motorista = st.selectbox("Motorista", options=opcoes_mot, format_func=lambda x: "Todos" if x == "Todos" else motorista_map[x], key="filtro_mot")
                
                with col_btn:
                    st.write("") # Espaço em branco para empurrar o botão para baixo e alinhar com os inputs
                    st.write("")
                    # O on_click chama a função que reseta a memória
                    st.button("🔄 Resetar", on_click=limpar_filtros, use_container_width=True)

            # Força a data inicial no calendário usando o valor da memória
            opcoes_calendario["initialDate"] = str(st.session_state["filtro_data"])
            
            eventos = []
            for reserva in dados_reservas:
                # 5. Lógica dos filtros buscando direto da memória
                if st.session_state["filtro_veic"] != "Todos" and reserva["Veiculo_id"] != st.session_state["filtro_veic"]:
                    continue
                    
                if st.session_state["filtro_mot"] != "Todos" and reserva.get("id_motorista") != st.session_state["filtro_mot"]:
                    continue
                
                eventos.append({
                    "id": reserva["id"],
                    "title": f"🚗 {reserva['motivo_locacao']}",
                    "start": reserva["data_retirada"],
                    "end": reserva["data_devolucao"],
                    "backgroundColor": "#FF4B4B", 
                    "borderColor": "#FF4B4B",     
                    "textColor": "#FFFFFF",       
                    "extendedProps": {
                        "motorista": motorista_map.get(reserva.get("id_motorista"), "N/A"),
                        "veiculo_nome": veiculo_map.get(reserva["Veiculo_id"], "Desconhecido"),
                        "veiculo_id": reserva["Veiculo_id"],
                        "motorista_nome": motorista_map.get(reserva.get("id_motorista"), "Desconhecido")
                    }
                })
                
            # A chave dinâmica garante que o calendário acompanhe os botões
            chave_dinamica = f"calendario_{st.session_state['filtro_data']}_{st.session_state['filtro_veic']}_{st.session_state['filtro_mot']}"
            
            state = st_cal.calendar(events=eventos, options=opcoes_calendario, custom_css=css_brabo, key=chave_dinamica)

            if "eventClick" in state:
                mostrar_detalhes(state["eventClick"])       
        
            if st.button(f"**Cadastrar nova reserva**", icon="➕", type="secondary", use_container_width=True):
                st.session_state["pagina"] = "cadastro_reserva"
                st.rerun()
                
        case "veiculos":
            # Dividimos o topo para colocar um botão de atualização ao lado do título
            st.title("Veículos PMAP")

            dados_veiculos = buscar_veiculos() # Puxa da memória
            dados_reservas = buscar_reservas() # Puxa da memória 
            
            for veiculo in dados_veiculos:
                with st.container(border=True):  
                    col1, col2, col3 = st.columns([1,2, 1], gap="medium")
                                    
                    with col1:
                        # Usando .get() para evitar erro caso não tenha ícone cadastrado
                        st.image(veiculo.get("Icone", "https://via.placeholder.com/150"))
                        
                    with col2:
                        st.subheader(veiculo["Modelo"])
                        st.write(f"Placa: {veiculo['Placa']}")  
                        st.write(f"Status: {veiculo['Status']}")
                        st.write(f"Referência: {veiculo['Referencia']}")
                    
                    with col3:
                        # Filtra apenas reservas ativas (futuras ou acontecendo agora) para exibir
                        hoje_iso = datetime.datetime.now().isoformat()
                        reserva_ativa = next(
                            (r for r in dados_reservas 
                             if r["Veiculo_id"] == veiculo["id"] and r["data_devolucao"] >= hoje_iso), 
                            None
                        )
                        
                        if veiculo["Status"] == "Disponível":
                            st.success("Disponível para reserva")
                        elif veiculo["Status"] == "Reservado":
                            st.warning("Reservado")
                            reservas_do_veiculo = [r for r in dados_reservas if r["Veiculo_id"] == veiculo["id"]]
                            if reservas_do_veiculo:
                                st.write("Reservas:")
                                for r in reservas_do_veiculo:
                                    data_inicio = datetime.datetime.fromisoformat(r['data_retirada']).strftime("%d/%m/%Y")
                                    data_fim = datetime.datetime.fromisoformat(r['data_devolucao']).strftime("%d/%m/%Y")
                                    st.write(f"- {data_inicio} a {data_fim}: {r['motivo_locacao']}")
                            else:
                                st.write("Nenhuma reserva encontrada.")
                        elif veiculo["Status"] == "Manutenção":
                            st.error("Em manutenção")
            
            
            
        case "motoristas":
            st.title("Página de Motoristas")
            
            dados_motoristas = buscar_motoristas() # Puxa da memória
            todas_reservas = buscar_reservas()     # Puxa da memória para não consultar no loop!
            
            import ast # Biblioteca nativa do Python para ajudar a ler os telefones antigos
            
            for motorista in dados_motoristas:
                with st.container(border=True):  
                    col1, col2, col3 = st.columns([1,1,1], gap="medium")
                                    
                    with col1:
                        # Substituímos o st.image() por HTML/CSS para forçar um corte perfeito de 150x150
                        st.markdown(f'''
                            <img src="{motorista['Foto_perfil']}" 
                                 style="width: 150px; height: 150px; object-fit: cover; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        ''', unsafe_allow_html=True)
                        
                    with col2:
                        st.subheader(motorista["Nome"])
                        st.write(f"ID: {motorista['id']}")
                        
                        # --- TRATAMENTO DO TELEFONE ---
                        telefone_exibicao = motorista['Telefone']
                        # Se o texto no banco começar com "{'type':", ele "desempacota" e pega só o número
                        if "{'type':" in telefone_exibicao:
                            try:
                                tel_dict = ast.literal_eval(telefone_exibicao)
                                telefone_exibicao = tel_dict.get('number', telefone_exibicao)
                            except:
                                pass
                                
                        st.write(f"Telefone: {telefone_exibicao}")
                        
                    with col3:
                        st.write("Reserva atual:")
                        reserva_atual = [r for r in todas_reservas if r.get("id_motorista") == motorista["id"]]
                        
                        if reserva_atual:
                            # Pega a primeira reserva encontrada
                            reserva = reserva_atual[0]
                            st.write(f"Motivo da locação: {reserva['motivo_locacao']}")
                            st.write(f"Data de início: {reserva['data_retirada']}")
                            st.write(f"Data de término: {reserva['data_devolucao']}")
                        else:
                            st.write("Nenhuma reserva ativa.")

            st.subheader("Cadastrar novo Motorista: ")
            with st.form("Formulário de Motorista", clear_on_submit=True):
                nome = st.text_input("Nome Completo")
                telefone = st_phone_number("Telefone", default_country="BR")
                
                foto_perfil = st.file_uploader("Foto de Perfil", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Salvar Motorista"):
                    if nome and telefone and foto_perfil:
                        try:
                            # 1. Gera um carimbo de tempo único (ex: 20260309160013)
                            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                            
                            # 2. Cria o caminho misturando o tempo com o nome original do arquivo
                            caminho_foto = f"motoristas/{timestamp}_{foto_perfil.name}"
                            
                            # 3. Extrai os BYTES reais da imagem
                            bytes_foto = foto_perfil.getvalue()
                            
                            # 4. Faz o upload informando o tipo de arquivo
                            supabase.storage.from_("Imagens").upload(
                                path=caminho_foto, 
                                file=bytes_foto, 
                                file_options={"content-type": foto_perfil.type}
                            )
                            
                            # 5. Pega a URL pública
                            url_foto_obj = supabase.storage.from_("Imagens").get_public_url(caminho_foto)
                            
                            url_foto = url_foto_obj
                            if isinstance(url_foto_obj, dict):
                                url_foto = url_foto_obj.get("public_url", url_foto_obj)
                            elif hasattr(url_foto_obj, 'public_url'):
                                url_foto = url_foto_obj.public_url
                            
                            # --- CORREÇÃO DO TELEFONE AO SALVAR ---
                            # Se a biblioteca retornar o dicionário, a gente pega apenas o "number".
                            if isinstance(telefone, dict):
                                numero_limpo = telefone.get("number", "")
                            else:
                                numero_limpo = str(telefone)
                            
                            novo_motorista = {
                                "Nome": nome,
                                "Telefone": numero_limpo,
                                "Foto_perfil": url_foto
                            }
                            
                            supabase.table("Motoristas").insert(novo_motorista).execute()
                            
                            buscar_motoristas.clear() # Atualiza a memória
                            st.success("Motorista cadastrado com sucesso!")
                            
                        except Exception as e:
                            st.error(f"Erro ao salvar a foto ou cadastrar: {e}")
                    else:
                        st.error("Por favor, preencha todos os campos e envie uma foto.")
                       
        case "cadastro_reserva":
            st.title("Cadastrar Nova Reserva")
            lista_veiculos = buscar_veiculos()
            lista_motoristas = buscar_motoristas()
            lista_reservas = buscar_reservas()
            
            mapa_veiculos = {v["id"]: f"{v['Modelo']} ({v['Placa']})" for v in lista_veiculos} 
            status_map = {v["id"]: v["Status"] for v in lista_veiculos}
            mapa_motoristas = {m["id"]: m["Nome"] for m in lista_motoristas}
            
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
                    if data_retirada >= data_devolucao:
                        st.error("A data de retirada deve ser anterior à data de devolução.")
                    else:
                        # Verificar conflito de datas com o mesmo veículo
                        conflito = False
                        for reserva in lista_reservas:
                            if reserva["Veiculo_id"] == veiculo_id:
                                existing_start = datetime.datetime.fromisoformat(reserva["data_retirada"])
                                existing_end = datetime.datetime.fromisoformat(reserva["data_devolucao"])
                                if (data_retirada < existing_end) and (data_devolucao > existing_start):
                                    conflito = True
                                    break
                        if conflito:
                            st.error("Já existe uma reserva para este veículo no período selecionado.")
                        else:
                            nova_reserva = {
                                "motivo_locacao": motivo,
                                "data_retirada": data_retirada.isoformat(),
                                "data_devolucao": data_devolucao.isoformat(),
                                "Veiculo_id": veiculo_id,
                                "id_motorista": motorista_id
                            }
                            supabase.table("Reservas").insert(nova_reserva).execute()
                            
                            sincronizar_status_veiculo(veiculo_id)
                            
                            buscar_reservas.clear()
                            
                            st.session_state["pagina"] = "reservas"
                            st.rerun()
                            
        case "editar_reserva":
            st.title("Editar Reserva")
            reserva_id = st.session_state.get("reserva_em_edicao")
            
            # Se a pessoa caiu aqui sem clicar em uma reserva antes, devolve ela pro calendário
            if not reserva_id:
                st.session_state["pagina"] = "reservas"
                st.rerun()
                
            lista_reservas = buscar_reservas()
            lista_veiculos = buscar_veiculos()
            lista_motoristas = buscar_motoristas()
            
            # Busca todos os dados da reserva que foi clicada
            reserva_atual = next((r for r in lista_reservas if str(r["id"]) == str(reserva_id)), None)
            
            if not reserva_atual:
                st.error("Reserva não encontrada no banco de dados.")
                st.stop()
                
            mapa_veiculos = {v["id"]: f"{v['Modelo']} ({v['Placa']})" for v in lista_veiculos} 
            mapa_motoristas = {m["id"]: m["Nome"] for m in lista_motoristas}

            # Descobre a posição (índice) do veículo e motorista atuais para preencher a selectbox
            opcoes_veiculos = list(mapa_veiculos.keys())
            index_veiculo = opcoes_veiculos.index(reserva_atual["Veiculo_id"]) if reserva_atual["Veiculo_id"] in opcoes_veiculos else 0
            
            opcoes_motoristas = list(mapa_motoristas.keys())
            index_motorista = opcoes_motoristas.index(reserva_atual["id_motorista"]) if reserva_atual["id_motorista"] in opcoes_motoristas else 0

            # Transforma a string de data do banco de volta em um formato que o Streamlit entende
            try:
                inicio_default = datetime.datetime.fromisoformat(reserva_atual["data_retirada"])
                fim_default = datetime.datetime.fromisoformat(reserva_atual["data_devolucao"])
            except Exception:
                inicio_default = datetime.datetime.now()
                fim_default = datetime.datetime.now()

            with st.form("Formulário de Edição"):
                motivo = st.text_input("Motivo da Locação", value=reserva_atual["motivo_locacao"])
                
                # O parâmetro 'value' é responsável por preencher os campos com o que já estava salvo
                data_retirada = st.datetime_input("Data da Retirada", value=inicio_default, format="DD/MM/YYYY") 
                data_devolucao = st.datetime_input("Data da Devolução", value=fim_default, format="DD/MM/YYYY")
                
                veiculo_id = st.selectbox("Selecione o Veículo", options=opcoes_veiculos, format_func=lambda x: mapa_veiculos[x], index=index_veiculo)
                motorista_id = st.selectbox("Selecione o Motorista", options=opcoes_motoristas, format_func=lambda x: mapa_motoristas[x], index=index_motorista)
                
                if st.form_submit_button("Salvar Alterações"):
                    if data_retirada >= data_devolucao:
                        st.error("A data de retirada deve ser anterior à data de devolução.")
                    else:
                        conflito = False
                        for r in lista_reservas:
                            # A mágica aqui é: str(r["id"]) != str(reserva_id) 
                            # Isso impede que o sistema ache que a reserva está conflitando com ela mesma!
                            if str(r["id"]) != str(reserva_id) and r["Veiculo_id"] == veiculo_id:
                                existing_start = datetime.datetime.fromisoformat(r["data_retirada"])
                                existing_end = datetime.datetime.fromisoformat(r["data_devolucao"])
                                if (data_retirada < existing_end) and (data_devolucao > existing_start):
                                    conflito = True
                                    break
                                    
                        if conflito:
                            st.error("Já existe uma reserva para este veículo no período selecionado.")
                        else:
                            dados_atualizados = {
                                "motivo_locacao": motivo,
                                "data_retirada": data_retirada.isoformat(),
                                "data_devolucao": data_devolucao.isoformat(),
                                "Veiculo_id": veiculo_id,
                                "id_motorista": motorista_id
                            }
                            # UPDATE em vez de INSERT. O .eq("id", reserva_id) garante que só essa reserva será alterada.
                            supabase.table("Reservas").update(dados_atualizados).eq("id", reserva_id).execute()
                            
                            sincronizar_status_veiculo(veiculo_id)
                            
                            veiculo_antigo_id = reserva_atual["Veiculo_id"]
                            if veiculo_id != veiculo_antigo_id:
                                sincronizar_status_veiculo(veiculo_antigo_id)
                            
                            buscar_reservas.clear()
                            st.session_state["pagina"] = "reservas"
                            st.rerun()
                            
            # Botão fora do formulário para quem quiser desistir de editar
            if st.button("Voltar sem salvar"):
                st.session_state["pagina"] = "reservas"
                st.rerun()
                
        case "home":
            lista_reservas = buscar_reservas()
            st.subheader("Reservas atuais:")
            for reserva in lista_reservas:
                st.write(f"- {reserva['Veiculo_id']} - {reserva['data_retirada']} to {reserva['data_devolucao']}")
            
        case _:
            st.write("Página não encontrada.")

# --- Estrutura da UI ---
col1, col2 = st.columns([1, 4])

with col1:
    with st.container(border=True, height="stretch"):
        st.subheader("Menu")
        if st.button("Início", icon="🏠", use_container_width=True):
            st.session_state["pagina"] = "home"
            st.rerun() # Força a tela a atualizar na hora
        
        if st.button("Calendário de Reservas", icon="🗓️", use_container_width=True):
            st.session_state["pagina"] = "reservas"
            st.rerun() # Força a tela a atualizar na hora
            
        if st.button("Veículos", icon="🛻", use_container_width=True):
            st.session_state["pagina"] = "veiculos"
            st.rerun()
            
        if st.button("Motoristas", icon="👥", use_container_width=True):
            st.session_state["pagina"] = "motoristas"
            st.rerun()

with col2: 

    carregarPagina()

