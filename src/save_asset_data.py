import requests
import sqlite3

class AssetDataDB:
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._initialize_db()
        

    def _initialize_db(self):
        """Initialize database connection and create tables"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self._create_tables()
            print("DB INITIALISED")
    
    def __enter__(self):
        self._initialize_db()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    
    def _create_tables(self):
        """Create the assets table"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT UNIQUE NOT NULL,
                title TEXT,
                description TEXT,
                asset_type TEXT,
                initial_creation TEXT,
                last_modified TEXT,
                parent_asset_id TEXT NOT NULL,
                parent_asset_title TEXT,                     
                inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()
    
    def bulk_insert_into_table(self, asset_data):
        
        data_to_insert = [
            (
                asset.get('assetId'),
                asset.get('title'),
                asset.get('initialCreation'),
                asset.get('assetType'),
                asset.get('lastModified'),
                asset.get('parentAsset', {}).get('assetId'),
                asset.get('parentAsset', {}).get('title')
            )
            for asset in asset_data
        ]

        try:

            self.cursor.executemany('''
            INSERT OR REPLACE INTO assets 
            (asset_id, title, initial_creation, asset_type, last_modified, parent_asset_id, parent_asset_title)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', data_to_insert)
        
            self.conn.commit()
            print("DATA INSERTED")
        except Exception as e:
            print(e)
    
    def get_asset_id(self):
        try:

            self.cursor.execute('''
            SELECT asset_id FROM assets
            ''')
            result = self.cursor.fetchall()
            return result
            
        except Exception as e:
            print(e)


    def get_asset_id_by_parents(self, id):
        try:

            self.cursor.execute('''
            SELECT asset_id FROM assets
            WHERE parent_asset_id = ?
            ''', (id,))
            result = self.cursor.fetchall()
            return result

        except Exception as e:
            print(e)
    
    def get_asset_id_and_modified_date_by_parents(self, id):
        try:

            self.cursor.execute('''
            SELECT asset_id, last_modified FROM assets
            WHERE parent_asset_id = ?
            ''', (id,))
            result = self.cursor.fetchall()
            return result

        except Exception as e:
            print(e)
