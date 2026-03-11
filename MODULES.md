# Índice de Módulos

Guia rápido para encontrar funções e classes.

## 📁 config/settings.py
**Para**: Constantes, configurações globais

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `APP_TITLE` | str | Título da aplicação |
| `APP_ICON` | str | Ícone da abinha |
| `CALENDAR_OPTIONS` | dict | Config do FullCalendar |
| `COLOR_RESERVATION` | str | Cor de reservas (#) |
| `STATUS_DISPONIVEL` | str | "Disponível" |
| `STATUS_RESERVADO` | str | "Reservado" |
| `STATUS_MANUTENCAO` | str | "Manutenção" |
| `CACHE_TTL_*` | int | TTL em segundos (60) |
| `TABLE_*` | str | Nome das tabelas Supabase |
| `STORAGE_MOTORISTAS_PATH` | str | Caminho armazenamento |

---

## 📁 database/supabase.py
**Para**: Todas as operações com banco de dados

### Connection
```python
get_supabase_client() → Client
```

### Reservas
```python
fetch_reservas() → [dict]  # @cache_data(ttl=60)
insert_reserva(data: dict) → Response
update_reserva(id: str, data: dict) → Response
delete_reserva(id: str) → Response
clear_reservas_cache() → None
```

### Veículos
```python
fetch_veiculos() → [dict]  # @cache_data(ttl=60)
update_veiculo_status(id: str, status: str) → Response
clear_veiculos_cache() → None
```

### Motoristas
```python
fetch_motoristas() → [dict]  # @cache_data(ttl=60)
insert_motorista(data: dict) → Response
clear_motoristas_cache() → None
```

### Storage
```python
upload_imagem(path: str, bytes: bytes, type: str) → str  # Retorna URL
```

### Lógica
```python
sincronizar_status_veiculo(veiculo_id: str, reservas: [dict] = None) → None
```

---

## 📁 utils/date_utils.py
**Para**: Manipulação e conversão de datas

```python
agora_iso() → str                    # ISO datetime agora
agora() → datetime.datetime
para_iso(dt: datetime) → str
de_iso(iso_str: str) → datetime      # Seguro com try/except
para_formato_br(iso: str) → str      # "01/01/2026 10:30"
para_data_br(iso: str) → str         # "01/01/2026"
hoje() → date
tem_sobreposicao(i1, f1, i2, f2) → bool
```

---

## 📁 utils/formatters.py
**Para**: Formatação de dados para UI

```python
extrair_numero_telefone(raw) → str
formatar_veiculo(v: dict) → str      # "Modelo (Ref)"
criar_mapa_veiculos([dict]) → {id: str}
criar_mapa_motoristas([dict]) → {id: str}
formatar_reserva_para_calendario(r, mapa_v, mapa_m) → dict
exibir_reserva_no_calendario([dict], mapa_v, mapa_m, filtro_v, filtro_m) → [dict]
```

---

## 📁 ui/styles.py
**Para**: Estilos CSS

```python
CALENDAR_CSS: str  # CSS para FullCalendar
```

---

## 📁 ui/components/components.py
**Para**: Componentes Streamlit reutilizáveis

```python
@st.dialog
mostrar_detalhes(evento_info: dict) → None

exibir_foto_motorista(url: str) → None  # HTML + CSS
```

---

## 📁 ui/screens/home.py
**Tela**: Home / Dashboard

```python
renderizar() → None
```

---

## 📁 ui/screens/reservas.py
**Tela**: Calendário de Reservas com filtros

```python
renderizar() → None
```

---

## 📁 ui/screens/veiculos.py
**Tela**: Lista de Veículos

```python
renderizar() → None
```

---

## 📁 ui/screens/motoristas.py
**Tela**: Lista + Cadastro de Motoristas

```python
renderizar() → None
```

---

## 📁 ui/screens/cadastro_reserva.py
**Tela**: Formulário Nova Reserva

```python
renderizar() → None
```

---

## 📁 ui/screens/editar_reserva.py
**Tela**: Formulário Editar Reserva

```python
renderizar() → None
```

---

## 📁 main.py
**Para**: Ponto de entrada e navegação

```python
main() → None           # Renderiza screen atual
renderizar_sidebar() → None  # Menu lateral
```

---

## 🔗 Relações de Módulos

```
Não importa direto de Supabase? Use database/supabase.py!
Precisa converter data? Use utils/date_utils.py!
Precisa formatar? Use utils/formatters.py!
Precisa componente Streamlit? Use ui/components/components.py!
Precisa constante? Use config/settings.py!
```

---

## 🔍 Como Encontrar o Que Precisa

| Preciso... | Arquivo | Função |
|-----------|---------|--------|
| Buscar dados do BD | database/supabase | fetch_* |
| Inserir/Atualizar | database/supabase | insert_*/update_* |
| Converter/Formatar | utils/formatters | formatar_* |
| Manipular datas | utils/date_utils | de_iso/para_*, agora_* |
| Cores/Config | config/settings | COLOR_*, TABLE_* |
| Calendário CSS | ui/styles | CALENDAR_CSS |
| Dialog/Modal | ui/components | mostrar_detalhes |
| Renderizar tela | ui/screens | renderizar() |
| Navegar | main.py | st.session_state["pagina"] |

---

## 💡 Exemplos Rápidos

### Fetch dados e formatar
```python
from database.supabase import fetch_veiculos
from utils.formatters import criar_mapa_veiculos

veiculos = fetch_veiculos()
mapa = criar_mapa_veiculos(veiculos)
```

### Converter data
```python
from utils.date_utils import para_data_br

data_br = para_data_br(iso_string)  # "01/01/2026"
```

### Inserir e limpar cache
```python
from database.supabase import insert_reserva, clear_reservas_cache

insert_reserva(dados_novos)
clear_reservas_cache()
```

### Navegar
```python
st.session_state["pagina"] = "reservas"
st.rerun()
```

---

*Última atualização: 2026-03-11*
