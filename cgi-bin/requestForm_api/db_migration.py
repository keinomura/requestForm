#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime
import subprocess
import json
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

def backup_database():
    """データベースのバックアップを作成する"""
    print("データベースのバックアップを作成中...")
    
    # MySQLの場合
    if os.getenv('DATABASE_URL', '').startswith('mysql'):
        try:
            # backup_db.shスクリプトを実行
            subprocess.run(['bash', 'backup_db.sh'], check=True)
            print("バックアップが正常に作成されました")
            return True
        except subprocess.CalledProcessError as e:
            print(f"バックアップの作成に失敗しました: {e}")
            return False
    # SQLiteの場合
    elif os.getenv('DATABASE_URL', '').startswith('sqlite'):
        try:
            db_path = os.getenv('DATABASE_URL').replace('sqlite:///', '')
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{backup_dir}/backup_{timestamp}.db"
            
            # SQLiteデータベースをコピー
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"バックアップが正常に作成されました: {backup_path}")
            return True
        except Exception as e:
            print(f"バックアップの作成に失敗しました: {e}")
            return False
    else:
        print("サポートされていないデータベースタイプです")
        return False

def export_schema():
    """現在のデータベーススキーマをエクスポートする"""
    print("現在のスキーマをエクスポート中...")
    
    try:
        # MySQLの場合
        if os.getenv('DATABASE_URL', '').startswith('mysql'):
            db_url = os.getenv('DATABASE_URL')
            parts = db_url.replace('mysql+pymysql://', '').split('@')
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')
            
            user = user_pass[0]
            password = user_pass[1]
            host = host_db[0]
            db_name = host_db[1]
            
            schema_dir = "schema_versions"
            os.makedirs(schema_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            schema_file = f"{schema_dir}/schema_{timestamp}.sql"
            
            # スキーマのみをエクスポート（データなし）
            cmd = f"mysqldump -h {host} -u {user} -p{password} --no-data {db_name} > {schema_file}"
            subprocess.run(cmd, shell=True, check=True)
            print(f"スキーマが正常にエクスポートされました: {schema_file}")
            return schema_file
        
        # SQLiteの場合
        elif os.getenv('DATABASE_URL', '').startswith('sqlite'):
            schema_dir = "schema_versions"
            os.makedirs(schema_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            schema_file = f"{schema_dir}/schema_{timestamp}.sql"
            
            db_path = os.getenv('DATABASE_URL').replace('sqlite:///', '')
            
            # SQLiteのスキーマをエクスポート
            cmd = f"sqlite3 {db_path} .schema > {schema_file}"
            subprocess.run(cmd, shell=True, check=True)
            print(f"スキーマが正常にエクスポートされました: {schema_file}")
            return schema_file
        
        else:
            print("サポートされていないデータベースタイプです")
            return None
    
    except Exception as e:
        print(f"スキーマのエクスポートに失敗しました: {e}")
        return None

def apply_migration(migration_file):
    """マイグレーションスクリプトを適用する"""
    print(f"マイグレーションを適用中: {migration_file}")
    
    try:
        # マイグレーションファイルを読み込む
        with open(migration_file, 'r') as f:
            migration_data = json.load(f)
        
        # SQLAlchemyを使用してマイグレーションを適用
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        
        with app.app_context():
            # マイグレーションSQLを実行
            for sql in migration_data.get('sql_statements', []):
                db.session.execute(sql)
            
            db.session.commit()
            print("マイグレーションが正常に適用されました")
            return True
    
    except Exception as e:
        print(f"マイグレーションの適用に失敗しました: {e}")
        return False

def create_migration_template():
    """新しいマイグレーションファイルのテンプレートを作成する"""
    migrations_dir = "migrations"
    os.makedirs(migrations_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_file = f"{migrations_dir}/migration_{timestamp}.json"
    
    template = {
        "description": "マイグレーションの説明を入力してください",
        "sql_statements": [
            "-- ここにSQLステートメントを追加してください",
            "-- 例: ALTER TABLE Requests ADD COLUMN new_column VARCHAR(255);"
        ]
    }
    
    with open(migration_file, 'w') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"マイグレーションテンプレートが作成されました: {migration_file}")
    print("このファイルを編集して、必要なSQLステートメントを追加してください。")
    return migration_file

def main():
    parser = argparse.ArgumentParser(description='データベースマイグレーションツール')
    parser.add_argument('--backup', action='store_true', help='データベースのバックアップを作成する')
    parser.add_argument('--export-schema', action='store_true', help='現在のスキーマをエクスポートする')
    parser.add_argument('--create-migration', action='store_true', help='新しいマイグレーションテンプレートを作成する')
    parser.add_argument('--apply', type=str, help='指定したマイグレーションファイルを適用する')
    
    args = parser.parse_args()
    
    if args.backup:
        backup_database()
    
    if args.export_schema:
        export_schema()
    
    if args.create_migration:
        create_migration_template()
    
    if args.apply:
        # バックアップを作成してからマイグレーションを適用
        if backup_database():
            apply_migration(args.apply)
        else:
            print("バックアップの作成に失敗したため、マイグレーションを適用しません")

if __name__ == "__main__":
    main()
