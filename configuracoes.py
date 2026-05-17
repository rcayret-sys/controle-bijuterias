from database import conectar


def carregar_configuracoes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome_programa, icone_programa
        FROM configuracoes
        WHERE id = 1
    """)

    config = cursor.fetchone()
    conn.close()

    if config is None:
        return "Controle de Bijuterias", "💍"

    return config[0], config[1]


def salvar_configuracoes(nome_programa, icone_programa):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE configuracoes
        SET nome_programa = ?,
            icone_programa = ?
        WHERE id = 1
    """, (nome_programa, icone_programa))

    conn.commit()
    conn.close()
