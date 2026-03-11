# ControleDeFrota - PMAP

Sistema de gerenciamento de reservas de veículos para a PMAP (Platform Management and Planning).

## 📋 Descrição

Aplicação Streamlit para controle centralizado de reservas, veículos e motoristas com calendário interativo, integração com Supabase e interface responsiva para web e mobile.

## 🎯 Funcionalidades

- **Calendário de Reservas**: Visualização interativa com FullCalendar
- **Gestão de Veículos**: Cadastro e status em tempo real
- **Gestão de Motoristas**: Perfil com foto e histórico de reservas
- **Sistema de Filtros**: Por data, veículo e motorista
- **Sincronização Automática**: Atualização de status baseada em reservas ativas
- **Responsivo**: Otimizado para desktop e mobile

## 🏗️ Estrutura do Projeto

```
ControleDeFrota/
├── main.py                      # Ponto de entrada da aplicação
├── requirements.txt             # Dependências Python
├── .gitignore                   # Arquivos ignorados pelo Git
├── .streamlit/
│   └── config.toml             # Configuração do Streamlit
├── config/
│   └── settings.py             # Constantes e configurações
├── database/
│   └── supabase.py             # Operações com Supabase (cache, CRUD)
├── utils/
│   ├── __init__.py
│   ├── date_utils.py           # Funções de manipulação de datas
│   └── formatters.py           # Funções de formatação de dados
├── ui/
│   ├── __init__.py
│   ├── styles.py               # CSS customizado
│   ├── components/
│   │   ├── __init__.py
│   │   └── components.py       # Componentes reutilizáveis (diálogos, etc)
│   └── screens/
│       ├── __init__.py
│       ├── home.py             # Tela inicial
│       ├── reservas.py         # Calendário de reservas
│       ├── veiculos.py         # Lista de veículos
│       ├── motoristas.py       # Lista de motoristas
│       ├── cadastro_reserva.py # Formulário de nova reserva
│       └── editar_reserva.py   # Formulário de edição
└── README.md                    # Este arquivo
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- pip ou conda
- Credenciais Supabase (URL e Key)

### Passos

1. **Clone o repositório**
   ```bash
   git clone <repo-url>
   cd ControleDeFrota
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as credenciais Supabase**
   
   Crie o arquivo `.streamlit/secrets.toml`:
   ```toml
   SUPABASE_URL = "sua_url_aqui"
   SUPABASE_KEY = "sua_chave_aqui"
   ```

5. **Execute a aplicação**
   ```bash
   streamlit run main.py
   ```

## 📦 Dependências Principais

- **streamlit** (1.28.0+): Framework web
- **supabase** (2.3.0+): Cliente Supabase
- **streamlit_calendar** (0.1.0+): Componente de calendário
- **streamlit_phone_number** (0.0.14+): Input de telefone

## 🔧 Desenvolvimento

### Estrutura de Código

- **config/**: Centraliza constantes, configurações e mapeamentos
- **database/**: Abstrai todas as operações com Supabase (CRUD, cache clearing)
- **utils/**: Funções puras de formatação e manipulação de dados
- **ui/components/**: Componentes Streamlit reutilizáveis (diálogos, etc)
- **ui/screens/**: Telas separadas por funcionalidade
- **ui/styles.py**: Estilos CSS customizados

### Adicionando uma Nova Funcionalidade

1. Crie o arquivo em `ui/screens/` se for uma tela nova
2. Importe as funções necessárias de `database/` e `utils/`
3. Adicione a rota em `main.py`
4. Se precisar de caracteres/dados, atualize `config/settings.py`

## 📊 Estrutura do Banco de Dados (Supabase)

Tabelas esperadas:
- **Reservas**: id, motivo_locacao, data_retirada, data_devolucao, Veiculo_id, id_motorista
- **CadastroVeiculos**: id, Modelo, Placa, Status, Referencia, Icone
- **Motoristas**: id, Nome, Telefone, Foto_perfil

## 🎨 Customização

### Cores
Edite `config/settings.py`:
```python
COLOR_RESERVATION = "#FF4B4B"
COLOR_PRIMARY = "#fdcd2d"
```

### Estilos CSS
Edite `ui/styles.py` para customizar o calendário e componentes.

## 🐛 Troubleshooting

**Erro de conexão com Supabase:**
- Verifique se o arquivo `.streamlit/secrets.toml` existe
- Confirme URL e Key estão corretas

**Cache não atualiza:**
- O cache expira a cada 60 segundos por padrão
- Modifique `CACHE_TTL_*` em `config/settings.py`

**Importação de módulos:**
- Certifique-se de estar na pasta raiz do projeto
- Use `from` imports relatives: `from models.xyz import`

## 📝 Licença

Propriedade da PMAP.

## 👥 Autor

Desenvolvido com ❤️ para otimizar a gestão de frota.
