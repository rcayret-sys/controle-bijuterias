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
