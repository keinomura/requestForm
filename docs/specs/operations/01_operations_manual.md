# 運用マニュアル - 要望管理システム

## ドキュメント情報

| 項目 | 内容 |
|------|------|
| ドキュメント名 | 運用マニュアル |
| システム名 | 電子カルテシステム要望管理システム |
| バージョン | 1.0 |
| 作成日 | 2026-01-05 |
| 最終更新日 | 2026-01-05 |
| ステータス | 引き渡し版 |

## 目次

1. [運用概要](#1-運用概要)
2. [サーバー環境情報](#2-サーバー環境情報)
3. [デプロイ手順](#3-デプロイ手順)
4. [バックアップとリストア](#4-バックアップとリストア)
5. [監視とメンテナンス](#5-監視とメンテナンス)
6. [トラブルシューティング](#6-トラブルシューティング)
7. [緊急時対応](#7-緊急時対応)
8. [定期メンテナンス](#8-定期メンテナンス)

---

## 1. 運用概要

### 1.1 運用体制

| 役割 | 責任範囲 | 連絡先 |
|------|---------|--------|
| システム管理者 | サーバー管理、デプロイ、障害対応 | SE部 |
| データベース管理者 | DB保守、バックアップ確認 | SE部 |
| アプリケーション担当 | 機能追加、バグ修正 | SE部 |

### 1.2 稼働時間

- **通常稼働**: 24時間365日
- **計画停止**: 月1回程度（メンテナンス時）、事前告知必須

### 1.3 サービスレベル

| 項目 | 目標値 |
|------|--------|
| 稼働率 | 99%以上 |
| 応答時間 | 3秒以内（通常操作） |
| 障害復旧時間 | 4時間以内（重大障害） |

---

## 2. サーバー環境情報

### 2.1 本番環境

#### サーバー基本情報

| 項目 | 内容 |
|------|------|
| ホスティング | さくらインターネット レンタルサーバー |
| ドメイン | felddorf.sakura.ne.jp |
| アプリケーションURL | https://felddorf.sakura.ne.jp/requestForm/ |
| API URL | https://felddorf.sakura.ne.jp/requestForm_api/ |

#### SSH接続情報

```bash
# SSH接続コマンド
ssh [ユーザー名]@[サーバーホスト名]

# ホスト: [サーバーホスト名]
# ポート: 22
# ユーザー名: [さくらレンタルサーバーのアカウント名]
# パスワード: **別途セキュアに共有**
```

**セキュリティ注意事項**:
- SSH接続情報は厳重に管理し、パスワードマネージャーなどで別途共有
- パスワードは定期的に変更
- 公開鍵認証の使用を推奨

---

#### ディレクトリ構成

```
/home/[username]/
├── www/
│   ├── requestForm/              # フロントエンド（静的ファイル）
│   │   ├── index.html
│   │   └── assets/
│   │       ├── index-[hash].js
│   │       └── index-[hash].css
│   │
│   └── cgi-bin/                  # バックエンド（CGI）
│       ├── index.cgi
│       └── requestForm_api/
│           ├── app.py
│           ├── .env
│           ├── requirements.txt
│           ├── venv/
│           ├── migrations/
│           └── backups/
│
└── [その他のディレクトリ]
```

---

### 2.2 データベース情報

#### MySQL接続情報

| 項目 | 内容 |
|------|------|
| DBホスト | [MySQLホスト名] |
| データベース名 | [データベース名] |
| ユーザー名 | [DBユーザー名] |
| パスワード | **別途セキュアに共有** |
| 文字コード | utf8mb4 |
| MySQLバージョン | 5.7+ |

**注意**: 実際の接続情報は、パスワードマネージャーや暗号化されたファイルで別途共有してください。

**MySQL接続コマンド**:
```bash
mysql -h [MySQLホスト名] -u [DBユーザー名] -p [データベース名]
# パスワード入力: [別途共有されたパスワード]
```

---

### 2.3 環境変数

**本番環境設定** (`.env`):
```bash
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=mysql+pymysql://[DBユーザー名]:[DBパスワード]@[MySQLホスト名]/[データベース名]
API_PREFIX=/requestForm_api
```

**注意**: 実際の値は `.env_for_mySQL` ファイルを参照するか、別途共有された情報を使用してください。

**ファイルパス**: `~/www/cgi-bin/requestForm_api/.env`

---

### 2.4 ログファイル

| ログ種類 | パス | 説明 |
|---------|------|------|
| バックアップログ | `~/www/cgi-bin/requestForm_api/backups/backup_log.txt` | データベースバックアップの実行履歴 |
| Webサーバーログ | さくらレンタルサーバー管理画面で確認 | アクセスログ、エラーログ |
| アプリケーションログ | 現状なし（今後実装推奨） | Flask アプリケーションログ |

---

## 3. デプロイ手順

### 3.1 デプロイ前準備

#### チェックリスト

- [ ] 変更内容をGitでコミット・プッシュ済み
- [ ] ローカル環境でテスト完了
- [ ] デプロイ計画を関係者へ通知
- [ ] データベースのバックアップ取得完了
- [ ] メンテナンス告知（必要な場合）

---

### 3.2 フロントエンドのデプロイ

#### 3.2.1 ローカルでのビルド

```bash
# 1. プロジェクトディレクトリへ移動
cd /path/to/requestForm/frontend

# 2. 依存パッケージのインストール（初回または package.json 変更時）
npm install

# 3. 本番ビルド実行
npm run build

# 4. ビルド成果物の確認
ls -la dist/
# 以下のファイルが生成されることを確認:
# - index.html
# - assets/index-[hash].js
# - assets/index-[hash].css
```

#### 3.2.2 サーバーへのアップロード

**方法1: FTPクライアント使用（推奨）**

1. FTPクライアント（FileZilla等）を起動
2. 接続情報:
   - ホスト: `felddorf.sakura.ne.jp`
   - プロトコル: SFTP
   - ポート: 22
   - ユーザー名: [サーバーアカウント名]
   - パスワード: [サーバーパスワード]
3. ローカルの `dist/` フォルダ内のすべてのファイルを選択
4. サーバーの `~/www/requestForm/` へアップロード
5. 既存ファイルを上書き

**方法2: コマンドライン（scp/rsync）**

```bash
# scpコマンドでアップロード
scp -r dist/* [username]@felddorf.sakura.ne.jp:~/www/requestForm/

# または rsync（差分のみアップロード）
rsync -avz --delete dist/ [username]@felddorf.sakura.ne.jp:~/www/requestForm/
```

#### 3.2.3 デプロイ確認

```bash
# ブラウザでアクセスして動作確認
# URL: https://felddorf.sakura.ne.jp/requestForm/

# キャッシュクリア後に確認
# Chrome: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
# Firefox: Ctrl+F5 (Windows) / Cmd+Shift+R (Mac)
```

---

### 3.3 バックエンドのデプロイ

#### 3.3.1 SSH接続

```bash
ssh [username]@felddorf.sakura.ne.jp
```

#### 3.3.2 アプリケーションファイルの更新

**方法1: Gitプル（推奨）**

```bash
# アプリケーションディレクトリへ移動
cd ~/www/cgi-bin/requestForm_api

# Gitから最新コードを取得
git pull origin main

# または特定のブランチ
git pull origin [branch-name]
```

**方法2: ファイル直接アップロード**

```bash
# ローカルマシンから実行
scp app.py [username]@felddorf.sakura.ne.jp:~/www/cgi-bin/requestForm_api/

# または複数ファイル
scp -r cgi-bin/requestForm_api/*.py [username]@felddorf.sakura.ne.jp:~/www/cgi-bin/requestForm_api/
```

#### 3.3.3 依存パッケージの更新

```bash
# 仮想環境をアクティベート
cd ~/www/cgi-bin/requestForm_api
source venv/bin/activate

# requirements.txt が更新されている場合
pip install -r requirements.txt

# 仮想環境を終了
deactivate
```

#### 3.3.4 環境変数の確認

```bash
# .env ファイルの内容を確認
cat ~/www/cgi-bin/requestForm_api/.env

# 本番設定になっていることを確認
# FLASK_ENV=production
# FLASK_DEBUG=0
# DATABASE_URL=mysql+pymysql://...
```

#### 3.3.5 CGIスクリプトのパーミッション確認

```bash
# index.cgi が実行可能であることを確認
ls -la ~/www/cgi-bin/index.cgi

# 実行権限がない場合は付与
chmod 755 ~/www/cgi-bin/index.cgi
```

#### 3.3.6 デプロイ確認

```bash
# API エンドポイントの動作確認
curl https://felddorf.sakura.ne.jp/requestForm_api/requests

# 正常な場合、JSON形式で要望一覧が返却される
```

---

### 3.4 データベースマイグレーション

#### 3.4.1 マイグレーション適用

```bash
# SSHでサーバーに接続
ssh [username]@felddorf.sakura.ne.jp

# アプリケーションディレクトリへ移動
cd ~/www/cgi-bin/requestForm_api

# 仮想環境をアクティベート
source venv/bin/activate

# マイグレーション前にバックアップ
python db_migration.py --backup

# マイグレーションファイルの適用
python db_migration.py --apply migrations/[migration_file].json

# 仮想環境を終了
deactivate
```

#### 3.4.2 マイグレーションファイルの作成

**ローカル環境で作成**:

```bash
cd cgi-bin/requestForm_api

# マイグレーションテンプレート作成
python db_migration.py --create-migration

# 生成されたファイルを編集
# migrations/migration_YYYYMMDD_HHMMSS.json
```

**マイグレーションファイル例**:
```json
{
  "description": "Add new_column to Requests table",
  "sql_statements": [
    "ALTER TABLE Requests ADD COLUMN new_column VARCHAR(255);"
  ]
}
```

---

### 3.5 デプロイ完了チェックリスト

- [ ] フロントエンドが正しく表示される
- [ ] API エンドポイントが応答する
- [ ] 要望一覧が表示される
- [ ] 新規要望登録が動作する
- [ ] 要望の更新が動作する
- [ ] 要望の削除が動作する（管理者モード）
- [ ] コメント履歴が表示される
- [ ] レスポンシブデザインが機能する（モバイル、タブレット確認）
- [ ] ブラウザコンソールにエラーがない
- [ ] デプロイ完了を関係者へ通知

---

## 4. バックアップとリストア

### 4.1 バックアップの種類

| バックアップ種類 | 対象 | 頻度 | 保持期間 |
|---------------|------|------|---------|
| データベースバックアップ | MySQL (Requests, Responses) | 毎日自動 | 30日間 |
| アプリケーションコード | Flask API, Vue.js | Git管理 | 無期限 |
| 環境設定ファイル | .env | 手動 | 無期限（別途管理） |

---

### 4.2 データベースバックアップ

#### 4.2.1 自動バックアップ設定

**バックアップスクリプト**: `~/www/cgi-bin/requestForm_api/backup_db.sh`

**スクリプト内容**:
```bash
#!/bin/bash

# データベース接続情報
DB_USER="[DBユーザー名]"
DB_HOST="[MySQLホスト名]"
DB_NAME="[データベース名]"
DB_PASSWORD="[DBパスワード]"

# バックアップディレクトリ
BACKUP_DIR="./backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# バックアップ実行
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_FILE

# 圧縮
gzip $BACKUP_FILE

# 30日以上古いバックアップを削除
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# ログ記録
echo "$(date): Backup completed - $BACKUP_FILE.gz" >> $BACKUP_DIR/backup_log.txt
```

**cron設定（推奨）**:

```bash
# crontab を編集
crontab -e

# 以下を追加（毎日午前3時にバックアップ実行）
0 3 * * * cd /home/[username]/www/cgi-bin/requestForm_api && bash backup_db.sh
```

---

#### 4.2.2 手動バックアップ

**SSH経由での実行**:

```bash
# サーバーに接続
ssh [username]@felddorf.sakura.ne.jp

# スクリプトディレクトリへ移動
cd ~/www/cgi-bin/requestForm_api

# バックアップスクリプト実行
bash backup_db.sh

# バックアップファイル確認
ls -lh backups/
```

**ローカルマシンから実行**:

```bash
# mysqldump を使用してバックアップ取得
mysqldump -h [MySQLホスト名] \
          -u [DBユーザー名] \
          -p \
          [データベース名] > backup_$(date +%Y%m%d).sql

# パスワード入力: [DBパスワード]

# 圧縮
gzip backup_$(date +%Y%m%d).sql
```

---

#### 4.2.3 バックアップの確認

```bash
# バックアップログの確認
cat ~/www/cgi-bin/requestForm_api/backups/backup_log.txt

# 最新10件のバックアップログを表示
tail -n 10 ~/www/cgi-bin/requestForm_api/backups/backup_log.txt

# バックアップファイル一覧
ls -lh ~/www/cgi-bin/requestForm_api/backups/
```

---

### 4.3 データベースリストア

#### 4.3.1 リストア前の準備

```bash
# 1. 現在のデータベースをバックアップ
mysqldump -h [MySQLホスト名] \
          -u [データベース名] \
          -p \
          [データベース名] > pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql

# 2. バックアップファイルを解凍
cd ~/www/cgi-bin/requestForm_api/backups
gunzip backup_YYYYMMDD_HHMMSS.sql.gz
```

#### 4.3.2 リストア実行

**方法1: MySQL コマンドでリストア**

```bash
# データベースに接続してリストア
mysql -h [MySQLホスト名] \
      -u [データベース名] \
      -p \
      [データベース名] < backup_YYYYMMDD_HHMMSS.sql

# パスワード入力: [DBパスワード]
```

**方法2: データベース再作成後にリストア**

```bash
# MySQLに接続
mysql -h [MySQLホスト名] -u [データベース名] -p

# データベース内で実行
DROP DATABASE IF EXISTS [データベース名];
CREATE DATABASE [データベース名] CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE [データベース名];
SOURCE /path/to/backup_YYYYMMDD_HHMMSS.sql;
EXIT;
```

#### 4.3.3 リストア後の確認

```bash
# データベースに接続
mysql -h [MySQLホスト名] -u [データベース名] -p [データベース名]

# テーブル一覧確認
SHOW TABLES;

# レコード件数確認
SELECT COUNT(*) FROM Requests;
SELECT COUNT(*) FROM Responses;

# 最新データ確認
SELECT * FROM Requests ORDER BY update_date DESC LIMIT 5;

# 終了
EXIT;
```

---

### 4.4 アプリケーションコードのバックアップ

#### 4.4.1 Git管理

**リポジトリ**: https://github.com/keinomura/requestForm.git

**バックアップ手順**:
```bash
# ローカルで変更をコミット
git add .
git commit -m "バックアップ: [変更内容]"

# リモートリポジトリへプッシュ
git push origin main
```

#### 4.4.2 手動バックアップ

```bash
# サーバー上のアプリケーションコードをアーカイブ
cd ~/www/cgi-bin
tar -czf requestForm_api_backup_$(date +%Y%m%d).tar.gz requestForm_api/

# ローカルマシンへダウンロード
scp [username]@felddorf.sakura.ne.jp:~/www/cgi-bin/requestForm_api_backup_*.tar.gz ./
```

---

## 5. 監視とメンテナンス

### 5.1 日次監視項目

| 項目 | 確認方法 | 正常基準 |
|------|---------|---------|
| サイトアクセス可能性 | https://felddorf.sakura.ne.jp/requestForm/ へアクセス | 200 OK、画面表示 |
| API応答 | `curl https://felddorf.sakura.ne.jp/requestForm_api/requests` | JSON応答 |
| データベース接続 | MySQL接続確認 | 接続成功 |
| バックアップ実施 | backup_log.txt確認 | 毎日バックアップ記録あり |

**監視スクリプト例**:

```bash
#!/bin/bash
# ~/www/cgi-bin/requestForm_api/health_check.sh

# サイトアクセスチェック
SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://felddorf.sakura.ne.jp/requestForm/)
if [ $SITE_STATUS -eq 200 ]; then
  echo "$(date): Site OK" >> health_check.log
else
  echo "$(date): Site ERROR - Status: $SITE_STATUS" >> health_check.log
fi

# API チェック
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://felddorf.sakura.ne.jp/requestForm_api/requests)
if [ $API_STATUS -eq 200 ]; then
  echo "$(date): API OK" >> health_check.log
else
  echo "$(date): API ERROR - Status: $API_STATUS" >> health_check.log
fi
```

---

### 5.2 週次メンテナンス

- [ ] バックアップログの確認
- [ ] ディスク使用量の確認
- [ ] エラーログの確認
- [ ] アクセスログの分析

**ディスク使用量確認**:

```bash
# ホームディレクトリの使用量
du -sh ~/www/

# バックアップディレクトリの使用量
du -sh ~/www/cgi-bin/requestForm_api/backups/

# データベースサイズ確認
mysql -h [MySQLホスト名] -u [データベース名] -p -e "
SELECT
  table_schema AS 'Database',
  SUM(data_length + index_length) / 1024 / 1024 AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = '[データベース名]'
GROUP BY table_schema;
"
```

---

### 5.3 月次メンテナンス

- [ ] 依存パッケージのアップデート確認
- [ ] セキュリティパッチ適用
- [ ] パフォーマンスレビュー
- [ ] バックアップのリストアテスト

**依存パッケージの更新**:

**フロントエンド**:
```bash
cd frontend
npm outdated
npm update
npm audit fix
```

**バックエンド**:
```bash
cd cgi-bin/requestForm_api
source venv/bin/activate
pip list --outdated
pip install --upgrade [package-name]
deactivate
```

---

## 6. トラブルシューティング

### 6.1 よくある問題と解決方法

#### 6.1.1 サイトが表示されない（404 Not Found）

**症状**: https://felddorf.sakura.ne.jp/requestForm/ にアクセスすると404エラー

**原因**:
1. ファイルがアップロードされていない
2. ファイルパスが間違っている

**解決方法**:
```bash
# SSH接続
ssh [username]@felddorf.sakura.ne.jp

# ファイルの存在確認
ls -la ~/www/requestForm/

# index.html が存在しない場合は再デプロイ
# ローカルから dist/ フォルダをアップロード
```

---

#### 6.1.2 API が応答しない（500 Internal Server Error）

**症状**: API エンドポイントにアクセスすると500エラー

**原因**:
1. Pythonスクリプトにエラーがある
2. 環境変数が正しく設定されていない
3. データベース接続エラー
4. CGI スクリプトのパーミッションエラー

**解決方法**:

```bash
# 1. エラーログ確認
# さくらレンタルサーバー管理画面からエラーログを確認

# 2. CGI スクリプトのパーミッション確認
ls -la ~/www/cgi-bin/index.cgi
chmod 755 ~/www/cgi-bin/index.cgi

# 3. 環境変数確認
cat ~/www/cgi-bin/requestForm_api/.env

# 4. データベース接続テスト
cd ~/www/cgi-bin/requestForm_api
source venv/bin/activate
python3 -c "
from app import db
print(db.engine.url)
"

# 5. 手動でアプリ起動テスト（開発モード）
python3 app.py
```

---

#### 6.1.3 データベース接続エラー

**症状**: `Can't connect to MySQL server` エラー

**原因**:
1. データベース接続情報が間違っている
2. MySQLサーバーがダウンしている
3. ネットワークの問題

**解決方法**:

```bash
# 1. MySQL接続テスト
mysql -h [MySQLホスト名] \
      -u [データベース名] \
      -p \
      [データベース名]

# 接続できない場合:
# - パスワードが正しいか確認
# - さくらインターネットの障害情報を確認
# - データベースホスト名が正しいか確認

# 2. .env ファイルの DATABASE_URL を確認
cat ~/www/cgi-bin/requestForm_api/.env | grep DATABASE_URL

# 3. PyMySQL がインストールされているか確認
source ~/www/cgi-bin/requestForm_api/venv/bin/activate
pip list | grep PyMySQL
```

---

#### 6.1.4 要望一覧が表示されない

**症状**: 画面は表示されるが要望一覧が空

**原因**:
1. APIとの通信エラー
2. CORSエラー
3. データベースにデータがない

**解決方法**:

```bash
# 1. ブラウザのコンソールを開いてエラー確認
#    Chrome: F12 → Consoleタブ
#    CORSエラーが表示されている場合、バックエンドのCORS設定を確認

# 2. API が応答しているか確認
curl https://felddorf.sakura.ne.jp/requestForm_api/requests

# 3. データベースにレコードがあるか確認
mysql -h [MySQLホスト名] -u [データベース名] -p [データベース名] -e "SELECT COUNT(*) FROM Requests;"

# 4. フロントエンドの API URL 設定を確認
# ~/www/requestForm/assets/index-[hash].js 内で
# VITE_API_URL が正しいか確認
```

---

#### 6.1.5 更新・削除ができない

**症状**: 更新ボタンを押しても反応がない、または削除ができない

**原因**:
1. パスワードが間違っている
2. 管理者モードがOFFになっている（削除の場合）
3. API エラー

**解決方法**:

```bash
# 1. パスワード確認
#    更新パスワード: [操作パスワード]
#    削除パスワード: [操作パスワード]

# 2. 管理者モードを確認（削除の場合）
#    画面右上の「管理者モード」スイッチをONにする

# 3. ブラウザコンソールでエラー確認
#    F12 → Console タブ

# 4. APIが正しく動作しているか確認
# 更新テスト
curl -X PUT https://felddorf.sakura.ne.jp/requestForm_api/requests/[uuid] \
     -H "Content-Type: application/json" \
     -d '{"status":"覚知(対応中)"}'

# 削除テスト
curl -X DELETE https://felddorf.sakura.ne.jp/requestForm_api/requests/[uuid]
```

---

#### 6.1.6 日時表示がおかしい

**症状**: 登録日時や更新日時が9時間ずれている

**原因**: タイムゾーン変換が正しく機能していない

**解決方法**:

```python
# app.py の確認
# 以下のコードがあることを確認
from datetime import datetime, timezone, timedelta

jst = timezone(timedelta(hours=9))

# to_dict() メソッド内で JST 変換が行われているか確認
def to_dict(self):
    return {
        'input_date': self.input_date.replace(tzinfo=timezone.utc).astimezone(jst).isoformat() if self.input_date else None,
        # ...
    }
```

---

### 6.2 エラーログの確認方法

#### 6.2.1 Webサーバーエラーログ

**さくらレンタルサーバー管理画面で確認**:

1. さくらインターネット会員メニューにログイン
2. 「サーバー情報」→「エラーログ」を選択
3. 最新のエラーを確認

#### 6.2.2 アプリケーションログ

現状、アプリケーションログは実装されていません。

**今後の実装推奨**:

```python
# app.py に追加
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

@app.route('/requests', methods=['POST'])
def create_request():
    try:
        # 処理
        logging.info(f'Request created: {new_request.request_uuid}')
    except Exception as e:
        logging.error(f'Error creating request: {str(e)}')
        return jsonify({'error': str(e)}), 500
```

---

## 7. 緊急時対応

### 7.1 緊急連絡体制

| 障害レベル | 定義 | 連絡先 | 対応時間 |
|-----------|------|--------|---------|
| レベル1（軽微） | 一部機能が使えない | SE部（営業時間内） | 翌営業日中 |
| レベル2（重大） | サイト全体が使えない | SE部（即時連絡） | 4時間以内 |
| レベル3（致命的） | データ損失の可能性 | SE部長（即時連絡） | 1時間以内 |

### 7.2 緊急時対応フロー

```
[障害発生]
    ↓
① 障害レベルの判定
    ↓
② 関係者へ連絡
    ↓
③ 暫定対応（可能な場合）
    ↓
④ 原因調査
    ↓
⑤ 恒久対策
    ↓
⑥ 事後報告書作成
```

### 7.3 緊急時の暫定対応

#### 7.3.1 サービス停止（メンテナンスモード）

**方法1: index.html を一時的に差し替え**

```bash
# SSH接続
ssh [username]@felddorf.sakura.ne.jp

# 現在の index.html をバックアップ
cd ~/www/requestForm
mv index.html index.html.bak

# メンテナンス用 HTML を作成
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>メンテナンス中</title>
</head>
<body style="text-align:center; padding-top:100px;">
  <h1>現在メンテナンス中です</h1>
  <p>ご不便をおかけして申し訳ございません。</p>
  <p>復旧まで今しばらくお待ちください。</p>
</body>
</html>
EOF

# メンテナンス終了後、元に戻す
mv index.html.bak index.html
```

---

#### 7.3.2 データベースのロールバック

```bash
# 最新のバックアップを確認
ls -lht ~/www/cgi-bin/requestForm_api/backups/ | head -n 5

# バックアップからリストア
cd ~/www/cgi-bin/requestForm_api/backups
gunzip backup_YYYYMMDD_HHMMSS.sql.gz

mysql -h [MySQLホスト名] \
      -u [データベース名] \
      -p \
      [データベース名] < backup_YYYYMMDD_HHMMSS.sql
```

---

#### 7.3.3 アプリケーションのロールバック

```bash
# Git で前のバージョンに戻す
cd ~/www/cgi-bin/requestForm_api

# コミット履歴確認
git log --oneline -n 10

# 特定のコミットに戻す
git checkout [commit-hash]

# または、1つ前のコミットに戻す
git reset --hard HEAD~1
```

---

### 7.4 障害報告書テンプレート

```markdown
# 障害報告書

## 障害情報
- 発生日時: YYYY/MM/DD HH:MM
- 検知日時: YYYY/MM/DD HH:MM
- 復旧日時: YYYY/MM/DD HH:MM
- 障害レベル: [レベル1/レベル2/レベル3]

## 影響範囲
- 影響を受けた機能:
- 影響を受けたユーザー数:

## 障害内容
- 症状:
- 原因:

## 対応内容
- 暫定対応:
- 恒久対策:

## 再発防止策
-

## 今後の改善点
-
```

---

## 8. 定期メンテナンス

### 8.1 月次メンテナンス計画

**実施タイミング**: 毎月第2土曜日 午前2:00〜4:00（予定）

**メンテナンス内容**:

- [ ] システムアップデート確認
- [ ] データベース最適化
- [ ] 不要ログの削除
- [ ] バックアップのリストアテスト
- [ ] セキュリティパッチ適用
- [ ] パフォーマンスチェック

---

### 8.2 データベース最適化

```bash
# MySQL に接続
mysql -h [MySQLホスト名] -u [データベース名] -p [データベース名]

# テーブル最適化
OPTIMIZE TABLE Requests;
OPTIMIZE TABLE Responses;

# インデックスの再構築
ANALYZE TABLE Requests;
ANALYZE TABLE Responses;

# テーブル状態確認
SHOW TABLE STATUS;

EXIT;
```

---

### 8.3 不要ログの削除

```bash
# SSH接続
ssh [username]@felddorf.sakura.ne.jp

# 30日以上古いバックアップファイルを削除
find ~/www/cgi-bin/requestForm_api/backups -name "backup_*.sql.gz" -mtime +30 -delete

# バックアップログのローテーション（1000行以上の場合）
cd ~/www/cgi-bin/requestForm_api/backups
if [ $(wc -l < backup_log.txt) -gt 1000 ]; then
  tail -n 500 backup_log.txt > backup_log_new.txt
  mv backup_log_new.txt backup_log.txt
fi
```

---

### 8.4 セキュリティチェック

```bash
# 依存パッケージの脆弱性スキャン（フロントエンド）
cd frontend
npm audit

# 重大な脆弱性がある場合は修正
npm audit fix

# 依存パッケージの更新（バックエンド）
cd cgi-bin/requestForm_api
source venv/bin/activate
pip list --outdated
pip install --upgrade [package-name]
```

---

### 8.5 パフォーマンスチェック

```bash
# データベースのレコード数確認
mysql -h [MySQLホスト名] -u [データベース名] -p [データベース名] -e "
SELECT
  'Requests' AS table_name, COUNT(*) AS record_count FROM Requests
UNION ALL
SELECT
  'Responses' AS table_name, COUNT(*) AS record_count FROM Responses;
"

# ディスク使用量確認
du -sh ~/www/

# API 応答時間測定
time curl https://felddorf.sakura.ne.jp/requestForm_api/requests > /dev/null
```

---

## 9. 付録

### 9.1 よく使うコマンド集

#### SSH接続
```bash
ssh [username]@felddorf.sakura.ne.jp
```

#### MySQL接続
```bash
mysql -h [MySQLホスト名] -u [データベース名] -p [データベース名]
```

#### データベースバックアップ
```bash
cd ~/www/cgi-bin/requestForm_api
bash backup_db.sh
```

#### ログ確認
```bash
tail -n 50 ~/www/cgi-bin/requestForm_api/backups/backup_log.txt
```

#### API動作確認
```bash
curl https://felddorf.sakura.ne.jp/requestForm_api/requests
```

#### ファイルアップロード（scp）
```bash
scp -r dist/* [username]@felddorf.sakura.ne.jp:~/www/requestForm/
```

---

### 9.2 緊急連絡先

| 項目 | 連絡先 |
|------|--------|
| SE部 | [電話番号] / [メールアドレス] |
| さくらインターネット サポート | https://support.sakura.ad.jp/ |
| システム管理者 | [担当者名] / [連絡先] |

---

### 9.3 関連ドキュメント

- [システム仕様書](../system/01_system_overview.md)
- [技術仕様書](../technical/01_technical_architecture.md)
- [開発環境構築手順書](../development/01_development_setup.md)
- GitHubリポジトリ: https://github.com/keinomura/requestForm.git

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|---------|--------|
| 1.0 | 2026-01-05 | 初版作成（引き渡し版） | - |

---

**以上**
