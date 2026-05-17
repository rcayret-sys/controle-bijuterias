from datetime import datetime
from database import executar, ler_df, obter_um

def registrar_entrada(produto_id, quantidade, observacao):
    data_entrada=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    executar("""INSERT INTO entradas_estoque (produto_id,data_entrada,quantidade,observacao) VALUES (:produto_id,:data_entrada,:quantidade,:observacao)""", {"produto_id":produto_id,"data_entrada":data_entrada,"quantidade":quantidade,"observacao":observacao})
    executar("""UPDATE produtos SET estoque=estoque+:quantidade WHERE id=:produto_id""", {"quantidade":quantidade,"produto_id":produto_id})

def carregar_entradas():
    return ler_df("""SELECT e.id AS "ID", e.data_entrada AS "Data", p.codigo AS "Código", p.descricao AS "Produto", e.quantidade AS "Quantidade", e.observacao AS "Observação" FROM entradas_estoque e INNER JOIN produtos p ON p.id=e.produto_id ORDER BY e.id DESC""")

def registrar_ajuste_estoque(produto_id, tipo_ajuste, quantidade, motivo):
    produto=obter_um("""SELECT estoque FROM produtos WHERE id=:produto_id""", {"produto_id":produto_id})
    if produto is None: return False, "Produto não encontrado."
    estoque_anterior=int(produto[0])
    if tipo_ajuste=="Entrada": estoque_novo=estoque_anterior+quantidade
    elif tipo_ajuste=="Saída":
        if quantidade > estoque_anterior: return False, f"Quantidade maior que o estoque atual: {estoque_anterior}"
        estoque_novo=estoque_anterior-quantidade
    else: estoque_novo=quantidade
    data_ajuste=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    executar("""INSERT INTO ajustes_estoque (produto_id,data_ajuste,tipo_ajuste,quantidade,estoque_anterior,estoque_novo,motivo) VALUES (:produto_id,:data_ajuste,:tipo_ajuste,:quantidade,:estoque_anterior,:estoque_novo,:motivo)""", {"produto_id":produto_id,"data_ajuste":data_ajuste,"tipo_ajuste":tipo_ajuste,"quantidade":quantidade,"estoque_anterior":estoque_anterior,"estoque_novo":estoque_novo,"motivo":motivo})
    executar("""UPDATE produtos SET estoque=:estoque_novo WHERE id=:produto_id""", {"estoque_novo":estoque_novo,"produto_id":produto_id})
    return True, f"Estoque ajustado. Anterior: {estoque_anterior} | Novo: {estoque_novo}"

def carregar_ajustes():
    return ler_df("""SELECT a.id AS "ID", a.data_ajuste AS "Data", p.codigo AS "Código", p.descricao AS "Produto", a.tipo_ajuste AS "Tipo", a.quantidade AS "Quantidade", a.estoque_anterior AS "Estoque Anterior", a.estoque_novo AS "Estoque Novo", a.motivo AS "Motivo" FROM ajustes_estoque a INNER JOIN produtos p ON p.id=a.produto_id ORDER BY a.id DESC""")
