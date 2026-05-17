import sqlite3

BANCO = "bijuterias.db"


def conectar():
    return sqlite3.connect(BANCO)


def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [info[1] for info in cursor.fetchall()]
    return coluna in colunas


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY,
            nome_programa TEXT,
            icone_programa TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO configuracoes (
            id,
            nome_programa,
            icone_programa
        )
        VALUES (1, 'Controle de Bijuterias', '💍')
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            ativo INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT,
            descricao TEXT NOT NULL,
            categoria TEXT,
            custo REAL DEFAULT 0,
            preco REAL DEFAULT 0,
            lucro REAL DEFAULT 0,
            estoque INTEGER DEFAULT 0
        )
    """)

    if not coluna_existe(cursor, "produtos", "ativo"):
        cursor.execute("ALTER TABLE produtos ADD COLUMN ativo INTEGER DEFAULT 1")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            data_venda TEXT,
            quantidade INTEGER,
            preco_unitario REAL,
            custo_unitario REAL,
            valor_total REAL,
            lucro_total REAL,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    if not coluna_existe(cursor, "vendas", "cancelada"):
        cursor.execute("ALTER TABLE vendas ADD COLUMN cancelada INTEGER DEFAULT 0")

    if not coluna_existe(cursor, "vendas", "data_cancelamento"):
        cursor.execute("ALTER TABLE vendas ADD COLUMN data_cancelamento TEXT")

    if not coluna_existe(cursor, "vendas", "motivo_cancelamento"):
        cursor.execute("ALTER TABLE vendas ADD COLUMN motivo_cancelamento TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            data_entrada TEXT,
            quantidade INTEGER,
            observacao TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ajustes_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            data_ajuste TEXT,
            tipo_ajuste TEXT,
            quantidade INTEGER,
            estoque_anterior INTEGER,
            estoque_novo INTEGER,
            motivo TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        for categoria in ["Brinco", "Colar", "Pulseira", "Anel", "Outro"]:
            cursor.execute(
                "INSERT INTO categorias (nome, ativo) VALUES (?, 1)",
                (categoria,)
            )

    conn.commit()
    conn.close()
