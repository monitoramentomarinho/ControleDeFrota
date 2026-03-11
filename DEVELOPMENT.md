# Guia Rápido de Desenvolvimento

## 🚀 Iniciar o Projeto

```bash
# Ativar ambiente virtual
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar a aplicação
streamlit run main.py
```

## 📋 Checklist: Adicionar Nova Funcionalidade

### Nova Tela Simples
- [ ] Criar arquivo em `ui/screens/nova_tela.py`
- [ ] Implementar função `renderizar()`
- [ ] Importar em `main.py`
- [ ] Adicionar entry no dict `screens`
- [ ] Adicionar botão na sidebar

### Nova Funcionalidade com BD
- [ ] Adicionar campos em `config/settings.py`
- [ ] Adicionar funções em `database/supabase.py`
- [ ] Adicionar formatadores em `utils/formatters.py`
- [ ] Usar na screen

### Corrigir Bug
- [ ] Localizar qual arquivo (main, database, utils, ui)
- [ ] Testas localmente
- [ ] Verificar se cache precisa ser limpo
- [ ] Testar em tela limpa (incógnito)

## 🔑 Padrões Importantes

### Importar dados
```python
from database.supabase import fetch_reservas, fetch_veiculos
dados = fetch_reservas()
```

### Formatar dados
```python
from utils.formatters import criar_mapa_veiculos
mapa = criar_mapa_veiculos(dados_veiculos)
```

### Manipular datas
```python
from utils.date_utils import para_data_br, agora_iso
data_formatada = para_data_br(iso_string)
```

### Exibir diálogo
```python
from ui.components.components import mostrar_detalhes
mostrar_detalhes(evento_info)
```

### Limpar cache após alteração
```python
from database.supabase import clear_* _cache
insert_novo_item(dados)
clear_reservas_cache()  # Limpa cache para atualizar
st.rerun()  # Recarrega a UI
```

## 🎨 Customizar Cores

Em `config/settings.py`:
```python
COLOR_RESERVATION = "#FF4B4B"
COLOR_PRIMARY = "#fdcd2d"
```

Em `ui/styles.py`:
```python
CALENDAR_CSS = """
    .fc-event {
        background-color: #FF4B4B !important;
    }
"""
```

## 🔍 Debug Comuns

### "ImportError: No module named X"
- Verifique se está no diretório correto
- Verifique se __init__.py existe nas pastas
- Teste rodar `python -c "import config"`

### "Supabase connection failed"
- Verifique `.streamlit/secrets.toml`
- Confirme SUPABASE_URL e SUPABASE_KEY
- Teste a conexão manualmente

### Cache não atualiza
- Procure por `.clear()` na screen
- Verifique se `st.rerun()` é chamado
- Tente refresh manual (F5)

### Componente Streamlit não aparece
- Verifique indentação
- Verifique se o arquivo `__init__.py` existe
- Verifique import statement

## 📊 Estrutura de uma Screen

```python
"""Descrição breve da tela."""
import streamlit as st
from database.supabase import fetch_x, insert_y
from utils.formatters import criar_mapa_x
from config.settings import SOME_CONSTANT

def renderizar():
    """Renderiza a tela."""
    # 1. Título
    st.title("Título da Tela")
    
    # 2. Fetch data
    dados = fetch_x()
    
    # 3. Preparar dados
    mapa = criar_mapa_x(dados)
    
    # 4. UI com filtros/forms
    with st.expander("Filtros"):
        filtro = st.selectbox("Opção", options=list(mapa.keys()))
    
    # 5. Lógica condicional
    dados_filtrados = [d for d in dados if d['id'] == filtro]
    
    # 6. Renderizar resultados
    for item in dados_filtrados:
        with st.container(border=True):
            st.write(item)
    
    # 7. Ações (submit, delete, etc)
    if st.button("Ação"):
        insert_y(dados_novos)
        clear_cache()  # Se modificou dados
        st.rerun()
```

## ⚡ Snippets Úteis

### Detectar re-run e sair
```python
if not reserva_id:
    st.session_state["pagina"] = "home"
    st.rerun()
```

### Converter string para datetime
```python
from utils.date_utils import de_iso
dt = de_iso(iso_string)  # Seguro mesmo se error
```

### Navegar entre screens
```python
st.session_state["pagina"] = "nova_pagina"
st.rerun()
```

### Validar checkbox (requer lista não vazia)
```python
if dados and filtro:
    # Fazer algo
else:
    st.error("Nenhum resultado")
```

### Exibir imagem com estilo
```python
st.markdown(f'''
    <img src="{url}" style="width: 100px; border-radius: 10px;">
''', unsafe_allow_html=True)
```

## 📚 Recursos

- Docs Streamlit: https://docs.streamlit.io/
- Docs Supabase: https://supabase.com/docs
- FullCalendar: https://fullcalendar.io/

## 🤝 Boas Práticas

✅ DO's:
- Separar lógica de renderização
- Usar nomes descritivos
- Documentar funções complexas
- Limpar cache após mudanças
- Usar type hints
- Organizar imports

❌ DON'Ts:
- Não colocar lógica no main.py
- Não chamar Supabase direto em screens
- Não deixar imports não usados
- Não usar variáveis globais
- Não committar secrets.toml
