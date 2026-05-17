import pandas as pd
from database import conectar


def carregar_categorias(apenas_ativas=False):
    conn = conectar()

    sql = """
        SELECT
            id AS ID,
            nome AS Categoria,
            CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END AS Status,
            ativo AS AtivoNum
        FROM categorias
    """

    if apenas_ativas:
        sql += " WHERE ativo = 1"

    sql += " ORDER BY nome"

    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


def salvar_categoria(nome):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO categorias (nome, ativo)
        VALUES (?, 1)
    """, (nome,))

    conn.commit()
    conn.close()


def atualizar_categoria(categoria_id, nome_antigo, nome_novo, ativo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE categorias
        SET nome = ?, ativo = ?
        WHERE id = ?
    """, (nome_novo, ativo, categoria_id))

    cursor.execute("""
        UPDATE produtos
        SET categoria = ?
        WHERE categoria = ?
    """, (nome_novo, nome_antigo))

    conn.commit()
    conn.close()


def categoria_em_uso(nome_categoria):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM produtos
        WHERE categoria = ?
    """, (nome_categoria,))

    qtd = cursor.fetchone()[0]
    conn.close()

    return qtd > 0


def excluir_categoria(categoria_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM categorias
        WHERE id = ?
    """, (categoria_id,))

    conn.commit()
    conn.close()
