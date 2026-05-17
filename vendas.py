from datetime import datetime
from database import executar, ler_df, obter_um

def registrar_venda(produto_id, quantidade):
    produto=obter_um("""SELECT descricao,custo,preco,estoque,ativo FROM produtos WHERE id=:produto_id""", {"produto_id":produto_id})
    if produto is None: return False, "Produto não encontrado."
    descricao,custo,preco,estoque_atual,ativo=produto
    if ativo != 1: return False, "Produto inativo. Venda não permitida."
    if quantidade > estoque_atual: return False, f"Estoque insuficiente. Estoque atual: {estoque_atual}"
    valor_total=preco*quantidade; lucro_total=(preco-custo)*quantidade; data_venda=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    executar("""INSERT INTO vendas (produto_id,data_venda,quantidade,preco_unitario,custo_unitario,valor_total,lucro_total,cancelada) VALUES (:produto_id,:data_venda,:quantidade,:preco_unitario,:custo_unitario,:valor_total,:lucro_total,0)""", {"produto_id":produto_id,"data_venda":data_venda,"quantidade":quantidade,"preco_unitario":preco,"custo_unitario":custo,"valor_total":valor_total,"lucro_total":lucro_total})
    executar("""UPDATE produtos SET estoque=estoque-:quantidade WHERE id=:produto_id""", {"quantidade":quantidade,"produto_id":produto_id})
    return True, f"Venda registrada: {quantidade} un. de {descricao}"

def carregar_vendas(incluir_canceladas=True):
    sql="""SELECT v.id AS "ID", v.data_venda AS "Data", p.codigo AS "Código", p.descricao AS "Produto", p.categoria AS "Categoria", v.quantidade AS "Quantidade", v.preco_unitario AS "Preço Unitário", v.custo_unitario AS "Custo Unitário", v.valor_total AS "Valor Total", v.lucro_total AS "Lucro Total", CASE WHEN v.cancelada = 1 THEN 'Cancelada' ELSE 'Ativa' END AS "Status", v.data_cancelamento AS "Data Cancelamento", v.motivo_cancelamento AS "Motivo Cancelamento", v.cancelada AS "CanceladaNum" FROM vendas v INNER JOIN produtos p ON p.id=v.produto_id"""
    if not incluir_canceladas: sql += " WHERE v.cancelada = 0"
    sql += " ORDER BY v.id DESC"
    return ler_df(sql)

def cancelar_venda(venda_id, motivo):
    venda=obter_um("""SELECT produto_id,quantidade,cancelada FROM vendas WHERE id=:venda_id""", {"venda_id":venda_id})
    if venda is None: return False, "Venda não encontrada."
    produto_id,quantidade,cancelada=venda
    if cancelada == 1: return False, "Esta venda já está cancelada."
    data_cancelamento=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    executar("""UPDATE vendas SET cancelada=1, data_cancelamento=:data_cancelamento, motivo_cancelamento=:motivo WHERE id=:venda_id""", {"data_cancelamento":data_cancelamento,"motivo":motivo,"venda_id":venda_id})
    executar("""UPDATE produtos SET estoque=estoque+:quantidade WHERE id=:produto_id""", {"quantidade":quantidade,"produto_id":produto_id})
    return True, "Venda cancelada e estoque devolvido com sucesso."
