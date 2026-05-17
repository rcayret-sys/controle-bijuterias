from pathlib import Path
from datetime import datetime
import shutil
BANCO_SQLITE="bijuterias.db"
PASTA_BACKUP="backups"

def criar_backup():
    origem=Path(BANCO_SQLITE)
    if not origem.exists(): return False, "Backup local disponível apenas quando usando SQLite local."
    pasta=Path(PASTA_BACKUP); pasta.mkdir(exist_ok=True)
    destino=pasta / f"backup_bijuterias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(origem,destino)
    return True, str(destino)
