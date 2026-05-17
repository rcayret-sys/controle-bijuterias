import pandas as pd
from database import conectar


def salvar_produto(codigo, descricao, categoria, custo, preco, estoque):
    lucro = preco - custo

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO produtos (
            codigo, descricao, categoria, custo, preco, lucro, estoque, ativo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (codigo, descricao, categoria, custo, preco, lucro, estoque))

    conn.commit()
    conn.close()


def atualizar_produto(produto_id, codigo, descricao, categoria, custo, preco, estoque, ativo):
    lucro = preco - custo

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE produtos
        SET
            codigo = ?,
            descricao = ?,
            categoria = ?,
            custo = ?,
            preco = ?,
            lucro = ?,
            estoque = ?,
            ativo = ?
        WHERE id = ?
    """, (
        codigo,
        descricao,
        categoria,
        custo,
        preco,
        lucro,
        estoque,
        ativo,
        produto_id
    ))

    conn.commit()
    conn.close()


def carregar_produtos():
    conn = conectar()

    df = pd.read_sql_query("""
        SELECT
            id AS ID,
            codigo AS Código,
            descricao AS Descrição,
            categoria AS Categoria,
            custo AS Custo,
            preco AS "Preço Venda",
            lucro AS "Lucro Unitário",
            estoque AS Estoque,
            CASE WHEN ativo = 1 THEN 'Ativo' ELSE 'Inativo' END AS Status,
            ativo AS AtivoNum
        FROM produtos
        ORDER BY descricao
    """, conn)

    conn.close()
    return df
