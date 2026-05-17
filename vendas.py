import pandas as pd
from datetime import datetime
from database import conectar


def registrar_venda(produto_id, quantidade):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT descricao, custo, preco, estoque, ativo
        FROM produtos
        WHERE id = ?
    """, (produto_id,))

    produto = cursor.fetchone()

    if produto is None:
        conn.close()
        return False, "Produto não encontrado."

    descricao, custo, preco, estoque_atual, ativo = produto

    if ativo != 1:
        conn.close()
        return False, "Produto inativo. Venda não permitida."

    if quantidade > estoque_atual:
        conn.close()
        return False, f"Estoque insuficiente. Estoque atual: {estoque_atual}"

    valor_total = preco * quantidade
    lucro_total = (preco - custo) * quantidade
    data_venda = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
        INSERT INTO vendas (
            produto_id, data_venda, quantidade, preco_unitario,
            custo_unitario, valor_total, lucro_total, cancelada
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        produto_id,
        data_venda,
        quantidade,
        preco,
        custo,
        valor_total,
        lucro_total
    ))

    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque - ?
        WHERE id = ?
    """, (quantidade, produto_id))

    conn.commit()
    conn.close()

    return True, f"Venda registrada: {quantidade} un. de {descricao}"


def carregar_vendas(incluir_canceladas=True):
    conn = conectar()

    sql = """
        SELECT
            v.id AS ID,
            v.data_venda AS Data,
            p.codigo AS Código,
            p.descricao AS Produto,
            p.categoria AS Categoria,
            v.quantidade AS Quantidade,
            v.preco_unitario AS "Preço Unitário",
            v.custo_unitario AS "Custo Unitário",
            v.valor_total AS "Valor Total",
            v.lucro_total AS "Lucro Total",
            CASE WHEN v.cancelada = 1 THEN 'Cancelada' ELSE 'Ativa' END AS Status,
            v.data_cancelamento AS "Data Cancelamento",
            v.motivo_cancelamento AS "Motivo Cancelamento",
            v.cancelada AS CanceladaNum
        FROM vendas v
        INNER JOIN produtos p ON p.id = v.produto_id
    """

    if not incluir_canceladas:
        sql += " WHERE v.cancelada = 0"

    sql += " ORDER BY v.id DESC"

    df = pd.read_sql_query(sql, conn)

    conn.close()
    return df


def cancelar_venda(venda_id, motivo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT produto_id, quantidade, cancelada
        FROM vendas
        WHERE id = ?
    """, (venda_id,))

    venda = cursor.fetchone()

    if venda is None:
        conn.close()
        return False, "Venda não encontrada."

    produto_id, quantidade, cancelada = venda

    if cancelada == 1:
        conn.close()
        return False, "Esta venda já está cancelada."

    data_cancelamento = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
        UPDATE vendas
        SET
            cancelada = 1,
            data_cancelamento = ?,
            motivo_cancelamento = ?
        WHERE id = ?
    """, (data_cancelamento, motivo, venda_id))

    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque + ?
        WHERE id = ?
    """, (quantidade, produto_id))

    conn.commit()
    conn.close()

    return True, "Venda cancelada e estoque devolvido com sucesso."
