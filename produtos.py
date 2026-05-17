from database import executar, ler_df

def salvar_produto(codigo, descricao, categoria, custo, preco, estoque):
    lucro = preco - custo
    executar("""INSERT INTO produtos (codigo, descricao, categoria, custo, preco, lucro, estoque, ativo) VALUES (:codigo,:descricao,:categoria,:custo,:preco,:lucro,:estoque,1)""", {"codigo":codigo,"descricao":descricao,"categoria":categoria,"custo":custo,"preco":preco,"lucro":lucro,"estoque":estoque})

def atualizar_produto(produto_id, codigo, descricao, categoria, custo, preco, estoque, ativo):
    lucro = preco - custo
    executar("""UPDATE produtos SET codigo=:codigo, descricao=:descricao, categoria=:categoria, custo=:custo, preco=:preco, lucro=:lucro, estoque=:estoque, ativo=:ativo WHERE id=:produto_id""", {"codigo":codigo,"descricao":descricao,"categoria":categoria,"custo":custo,"preco":preco,"lucro":lucro,"estoque":estoque,"ativo":ativo,"produto_id":produto_id})

def carregar_produtos():
    return ler_df("""SELECT id AS "ID", codigo AS "Código", descricao AS "Descrição", categoria AS "Categoria", custo AS "Custo", preco AS "Preço Venda", lucro AS "Lucro Unitário", estoque AS "Estoque", CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END AS "Status", ativo AS "AtivoNum" FROM produtos ORDER BY descricao""")
