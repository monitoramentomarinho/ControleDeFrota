# Arquitetura do ControleDeFrota

## 🎯 Princípios de Design

1. **Separação de Responsabilidades**: Cada módulo tem uma função específica
2. **Reutilização**: Componentes e funções reutilizáveis
3. **Manutenibilidade**: Código bem documentado e organizado
4. **Escalabilidade**: Fácil adicionar novas funcionalidades

## 📦 Camadas da Aplicação

### 1. **Entrada (main.py)**
- Ponto único de entrada
- Gerencia navegação entre telas
- Renderiza sidebar

### 2. **Configuração (config/)**
- `settings.py`: Constantes, configurações e mapeamentos
- Centraliza dados que podem mudar (cores, formatos, nomes de tabelas)

### 3. **Acesso a Dados (database/)**
- `supabase.py`: Abstração completa do Supabase
- Implementa caching com Streamlit decorators
- Funções de CRUD para cada entidade
- Sincronização automática de status

**Vantagens:**
- Uma única fonte de verdade para chamadas ao banco
- Cache configurável
- Fácil substituir Supabase por outro serviço

### 4. **Lógica de Negócio (utils/)**
- `date_utils.py`: Funções de data (conversão, comparação)
- `formatters.py`: Funções de formatação para UI

**Padrão:**
- Funções PURAS (sem side-effects)
- Testáveis
- Com type hints

### 5. **Componentes de UI (ui/components/)**
- `components.py`: Componentes Streamlit reutilizáveis
- Diálogos, cards, etc

**Características:**
- Encapsúlam lógica Streamlit
- Importáveis em qualquer screen

### 6. **Telas (ui/screens/)**
- `home.py`: Dashboard inicial
- `reservas.py`: Calendário com filtros
- `veiculos.py`: Lista e detalhes
- `motoristas.py`: Lista e cadastro
- `cadastro_reserva.py`: Formulário novo
- `editar_reserva.py`: Formulário edição

**Padrão:**
```python
def renderizar():
    # 1. Fetch data
    dados = fetch_x()
    
    # 2. Process (filtros, mapas)
    resultado = processar(dados)
    
    # 3. Render UI
    st.title(...)
    st.widget(...)
```

## 🔄 Fluxo de Dados

```
main.py (renderizar_sidebar + main)
    ↓
screens/*.py (renderizar)
    ↓
├─ database/supabase.py (fetch_*)
│  └─ Supabase API
│
├─ utils/formatters.py (criar_mapa_*, exibir_*)
│
├─ utils/date_utils.py (conversões)
│
└─ ui/components/components.py (UI reutilizável)
```

## 💾 Estratégia de Cache

```python
@st.cache_data(ttl=60)
def fetch_dados():
    return client.table(...).select(...).execute().data
```

**TTL padrão**: 60 segundos

**Clear cache**:
```python
fetch_dados.clear()  # Limpa o cache
```

**Usado em**:
- Quando salva/atualiza dados
- Sincronização de status

## ⚙️ Configurações Principais

Em `config/settings.py`:

| Variável | Uso |
|----------|-----|
| `APP_TITLE` | Título da aba do navegador |
| `CALENDAR_OPTIONS` | Configuração do FullCalendar |
| `CACHE_TTL_*` | Tempo de cache em segundos |
| `TABLE_*` | Nomes das tabelas Supabase |
| `STORAGE_*` | Caminho do armazenamento de imagens |

## 🔐 Segurança

- Credenciais em `.streamlit/secrets.toml` (NÃO commitado)
- `.gitignore` protege arquivos sensíveis
- Validço frontend (não substitute validação backend)

## 🧪 Testabilidade

**Funções testáveis:**
- `utils/date_utils.py` ✅
- `utils/formatters.py` ✅
- `database/supabase.py` (com mock) ✅

**Funções difíceis de testar:**
- Anything com `@st.cache_data`
- Anything com `st.button()`, `st.write()`

## 📈 Como Adicionar Funcionalidade

### 1. Nova Tela
```bash
# Criar arquivo
touch ui/screens/nova_tela.py

# Implementar
def renderizar():
    st.title("Nova Tela")
    # ...

# Adicionar rota em main.py
screens = {
    ...,
    "nova_tela": nova_tela.renderizar,
}

# Adicionar botão na sidebar
if st.button("Nova Tela", ...):
    st.session_state["pagina"] = "nova_tela"
    st.rerun()
```

### 2. Novo Campo em Entidade
```python
# 1. Atualizar config/settings.py
ENTIDADE_FIELDS = {
    "novo_campo": "Novo_Campo",  # BD
}

# 2. Atualizar database/supabase.py
# Adicionar novo parâmetro se necessário

# 3. Atualizar tela onde usa
# Adicionar novo st.input() ou st.write()
```

### 3. Nova Função Utilitária
```python
# Adicionar em utils/date_utils.py ou utils/formatters.py
def nova_funcao(param):
    """Documentação clara."""
    return resultado
```

## 🚀 Performance

**Otimizações implementadas:**
1. Cache com TTL de 60 segundos
2. Lazy loading de dados
3. Mapas pré-computados
4. Filtros no frontend

**Possíveis melhorias:**
- Paginação de resultados
- Índices no BD
- Compressão de imagens

## 📝 Logging

Atualmente sem logging estruturado. Para adicionar:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Evento importante")
```

## 🔗 Dependências Entre Módulos

```
main.py
├── ui.screens-* (todas as telas)
│   ├── database.supabase
│   ├── utils.formatters
│   ├── utils.date_utils
│   ├── ui.components
│   └── config.settings
├── ui.components
│   ├── database.supabase
│   └── utils.date_utils
└── config.settings

database.supabase
├── streamlit
├── supabase
└── config.settings

utils.*
├── config.settings (alguns)
└── datetime (stdlib)
```

**Sem ciclos circulares! ✅**
