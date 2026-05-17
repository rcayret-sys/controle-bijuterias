from database import executar, ler_df, obter_um

def carregar_categorias(apenas_ativas=False):
    sql="""SELECT id AS "ID", nome AS "Categoria", CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END AS "Status", ativo AS "AtivoNum" FROM categorias"""
    if apenas_ativas: sql += " WHERE ativo = 1"
    sql += " ORDER BY nome"
    return ler_df(sql)

def salvar_categoria(nome): executar("""INSERT INTO categorias (nome, ativo) VALUES (:nome,1)""", {"nome":nome})

def atualizar_categoria(categoria_id, nome_antigo, nome_novo, ativo):
    executar("""UPDATE categorias SET nome=:nome_novo, ativo=:ativo WHERE id=:categoria_id""", {"nome_novo":nome_novo,"ativo":ativo,"categoria_id":categoria_id})
    executar("""UPDATE produtos SET categoria=:nome_novo WHERE categoria=:nome_antigo""", {"nome_novo":nome_novo,"nome_antigo":nome_antigo})

def categoria_em_uso(nome_categoria):
    return obter_um("""SELECT COUNT(*) FROM produtos WHERE categoria=:nome_categoria""", {"nome_categoria":nome_categoria})[0] > 0

def excluir_categoria(categoria_id): executar("""DELETE FROM categorias WHERE id=:categoria_id""", {"categoria_id":categoria_id})
