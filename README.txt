Projeto Bijuterias - versão modular

Como testar:
1. Copie seu arquivo bijuterias.db para esta pasta, se quiser manter os dados atuais.
2. Abra o Prompt nesta pasta.
3. Execute:
   python -m streamlit run app.py

Ou dê duplo clique em abrir_app.bat.

Arquivos principais:
- app.py: interface do sistema
- database.py: criação do banco e conexão
- produtos.py: funções de produtos
- categorias.py: funções de categorias
- vendas.py: funções de vendas
- estoque.py: entradas e ajustes de estoque
- configuracoes.py: nome e ícone do sistema
- utils.py: formatações, exportação CSV, gráficos e filtros
- backup.py: rotina de backup


Correção: app.py recriado com apenas a interface, importando funções dos módulos.


Acesso por senha:
- O arquivo auth.py bloqueia o sistema até a senha ser digitada.
- No Streamlit Cloud, configure:
  App > Settings > Secrets

Conteúdo:
APP_PASSWORD = "sua_senha_aqui"

Importante:
- Não coloque sua senha real no GitHub.
- O arquivo .streamlit/secrets.toml.example é apenas exemplo.

Banco online: configure DATABASE_URL nos Secrets do Streamlit Cloud. Se não houver DATABASE_URL, usa SQLite local.


Otimização de performance:
- database.py agora usa st.cache_resource para reaproveitar a engine SQLAlchemy.
- Consultas de leitura usam st.cache_data com TTL de 20 segundos.
- Após gravações, o cache de leitura é limpo automaticamente.
- Foram adicionados índices básicos no PostgreSQL.
