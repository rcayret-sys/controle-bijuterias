import pandas as pd
from datetime import datetime
from database import conectar


def registrar_entrada(produto_id, quantidade, observacao):
    conn = conectar()
    cursor = conn.cursor()

    data_entrada = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
        INSERT INTO entradas_estoque (
            produto_id, data_entrada, quantidade, observacao
        )
        VALUES (?, ?, ?, ?)
    """, (produto_id, data_entrada, quantidade, observacao))

    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque + ?
        WHERE id = ?
    """, (quantidade, produto_id))

    conn.commit()
    conn.close()


def carregar_entradas():
    conn = conectar()

    df = pd.read_sql_query("""
        SELECT
            e.id AS ID,
            e.data_entrada AS Data,
            p.codigo AS Código,
            p.descricao AS Produto,
            e.quantidade AS Quantidade,
            e.observacao AS Observação
        FROM entradas_estoque e
        INNER JOIN produtos p ON p.id = e.produto_id
        ORDER BY e.id DESC
    """, conn)

    conn.close()
    return df


def registrar_ajuste_estoque(produto_id, tipo_ajuste, quantidade, motivo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT estoque
        FROM produtos
        WHERE id = ?
    """, (produto_id,))

    produto = cursor.fetchone()

    if produto is None:
        conn.close()
        return False, "Produto não encontrado."

    estoque_anterior = int(produto[0])

    if tipo_ajuste == "Entrada":
        estoque_novo = estoque_anterior + quantidade
    elif tipo_ajuste == "Saída":
        if quantidade > estoque_anterior:
            conn.close()
            return False, f"Quantidade maior que o estoque atual: {estoque_anterior}"
        estoque_novo = estoque_anterior - quantidade
    else:
        estoque_novo = quantidade

    data_ajuste = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
        INSERT INTO ajustes_estoque (
            produto_id,
            data_ajuste,
            tipo_ajuste,
            quantidade,
            estoque_anterior,
            estoque_novo,
            motivo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        produto_id,
        data_ajuste,
        tipo_ajuste,
        quantidade,
        estoque_anterior,
        estoque_novo,
        motivo
    ))

    cursor.execute("""
        UPDATE produtos
        SET estoque = ?
        WHERE id = ?
    """, (estoque_novo, produto_id))

    conn.commit()
    conn.close()

    return True, f"Estoque ajustado. Anterior: {estoque_anterior} | Novo: {estoque_novo}"


def carregar_ajustes():
    conn = conectar()

    df = pd.read_sql_query("""
        SELECT
            a.id AS ID,
            a.data_ajuste AS Data,
            p.codigo AS Código,
            p.descricao AS Produto,
            a.tipo_ajuste AS Tipo,
            a.quantidade AS Quantidade,
            a.estoque_anterior AS "Estoque Anterior",
            a.estoque_novo AS "Estoque Novo",
            a.motivo AS Motivo
        FROM ajustes_estoque a
        INNER JOIN produtos p ON p.id = a.produto_id
        ORDER BY a.id DESC
    """, conn)

    conn.close()
    return df
