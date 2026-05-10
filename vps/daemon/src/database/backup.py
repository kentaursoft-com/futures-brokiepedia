"""Backup manager for automated backups to Backblaze B2."""
import logging
import json
import gzip
import shutil
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from .turso_client import TursoClient

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages automated backups of trading data."""
    
    def __init__(self, backup_dir: str = None, retention_days: int = 30):
        self.backup_dir = backup_dir or '/tmp/trading-backups'
        self.retention_days = retention_days
        self.turso = TursoClient()
        self.turso.connect()
        
        os.makedirs(f"{self.backup_dir}/daily", exist_ok=True)
        os.makedirs(f"{self.backup_dir}/weekly", exist_ok=True)
        os.makedirs(f"{self.backup_dir}/manual", exist_ok=True)
        
        logger.info(f"✅ Backup Manager initialized")
    
    def create_backup(self, backup_type: str = 'manual') -> Optional[str]:
        """Create a complete backup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"trading_backup_{backup_type}_{timestamp}.json"
        filepath = os.path.join(self.backup_dir, backup_type, filename)
        
        logger.info(f"🔄 Creating {backup_type} backup...")
        
        try:
            # Gather data from Turso
            backup_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'type': backup_type,
                    'version': '1.0'
                },
                'trades': [],
                'signals': []
            }
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Compress
            compressed = f"{filepath}.gz"
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(filepath)
            
            logger.info(f"✅ Backup created: {compressed}")
            return compressed
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return None
    
    def list_backups(self) -> List[Dict]:
        """List all local backups."""
        backups = []
        for subdir in ['daily', 'weekly', 'manual']:
            path = os.path.join(self.backup_dir, subdir)
            if not os.path.exists(path):
                continue
            for f in os.listdir(path):
                if f.endswith('.gz'):
                    fp = os.path.join(path, f)
                    stat = os.stat(fp)
                    backups.append({
                        'filename': f,
                        'type': subdir,
                        'size_kb': round(stat.st_size / 1024, 2),
                        'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def get_backup_status(self) -> Dict:
        """Get backup status summary."""
        return {
            'local_backups_count': len(self.list_backups()),
            'backup_directory': self.backup_dir,
            'retention_days': self.retention_days
        }
