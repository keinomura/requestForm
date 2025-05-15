# 要望管理システム

## 概要
このシステムは、要望管理のためのウェブアプリケーションです。バックエンドはFlask、フロントエンドはVue.jsで構築されており、データベースにはさくらレンタルサーバーのMySQLを使用しています。

## 機能
- 要望の登録・一覧表示・検索
- 進捗状況の更新
- コメント履歴の管理
- 対応部署（会社）の管理

## システム構成
- バックエンド: Flask (Python)
- フロントエンド: Vue.js
- データベース: MySQL (さくらレンタルサーバー)

## セットアップ方法

### 開発環境

1. バックエンドのセットアップ
```bash
cd cgi-bin/requestForm_api
pip install -r requirements.txt
```

2. フロントエンドのセットアップ
```bash
cd frontend
npm install
```

3. 開発サーバーの起動
```bash
# バックエンド
cd cgi-bin/requestForm_api
python3 app.py

# フロントエンド
cd frontend
npm run dev
```

### 本番環境へのデプロイ

1. バックエンドのデプロイ
```bash
# さくらサーバーにファイルをアップロード
scp -r cgi-bin/* username@your-server.sakura.ne.jp:~/www/cgi-bin/
# 手作業でアップした。

# 環境設定ファイルを本番用に切り替え
ssh username@your-server.sakura.ne.jp "cp ~/www/cgi-bin/requestForm_api/.env_for_mySQL ~/www/cgi-bin/requestForm_api/.env"
# もともとサーバーに本番用ファイルが置いてある。
```


2. フロントエンドのビルドとデプロイ
```bash
# ビルド
cd frontend
npm run build

# さくらサーバーにファイルをアップロード
scp -r dist/* username@your-server.sakura.ne.jp:~/www/requestForm/
# 手作業でアップした。

```

## データベースバックアップと移行


### バックアップの実行


---

# さくらサーバーにSSH等でログインしてサーバー内で実行してください。
（ローカルPCから実行しても、MySQLに接続できない・権限エラーになる場合がほとんどです）

### さくらレンタルサーバーにSSHで接続する方法

1. **ターミナルを開く（Mac/Linuxの場合）またはコマンドプロンプト/PowerShellを開く（Windowsの場合）**

2. **以下のコマンドを実行します。**

ssh fe....rf@fe.....rf.sakura.ne.jp

- 「ユーザー名」は、さくらサーバーのコントロールパネルで確認できるSSHアカウント名です。
- 「サーバー名」は、契約しているサーバーのホスト名です。

3. **初回接続時は「yes」と入力して接続を許可します。**

4. **パスワードを入力します。**

- パスワードはサーバーパスワードです。bp..........bb


5. **接続が成功すると、サーバー内のコマンドライン操作が可能になります。**

```bash
# ファイルフォルダに移動
cd www

```

**補足：**
- パスワード認証ではなく、公開鍵認証を利用することもできます（推奨）。
- 詳細は[さくらのサポートページ](https://help.sakura.ad.jp/206151922/)も参照してください。

---

バックアップスクリプトを使用して、データベースのバックアップを作成します。


```bash
cd cgi-bin/requestForm_api
bash backup_db.sh
```

**注意**: 初回実行前に、`backup_db.sh`内の`BACKUP_DIR`変数を適切なバックアップディレクトリに設定してください。

- ./backupsに設定した。✓

### データベース移行ツールの使用方法

データベースのスキーマ変更を安全に行うための移行ツールを提供しています。

1. 現在のスキーマをエクスポート
```bash
python db_migration.py --export-schema
```

2. バックアップの作成
```bash
python db_migration.py --backup
```

3. 新しい移行ファイルの作成
```bash
python db_migration.py --create-migration
```

4. 移行の適用
/home/felddorf/www/cgi-bin/requestForm_api/migrations内にあるファイルを指定する。
migration_20250515_125441.json
```bash
python db_migration.py --apply migrations/migration_YYYYMMDD_HHMMSS.json
```
-> python db_migration.py --apply migrations/migration_20250515_125441.json


### 問題対応部署（会社）の追加

問題対応部署（会社）の項目を追加するための移行ファイルが用意されています。

```bash
python db_migration.py --apply migrations/migration_add_handler_company.json
```

## 時間表示の問題修正

バックエンド、フロントエンド、データベース間での時間表示の不整合を修正しました。すべての時間はUTCで保存され、表示時に日本時間（JST、UTC+9）に変換されます。

## レスポンシブデザインの改善

モバイル画面でのレイアウト問題を修正し、さまざまな画面サイズに対応するようにUIを改善しました。

## トラブルシューティング

### データベース接続エラー
- `.env`ファイルの`DATABASE_URL`が正しく設定されているか確認してください。
- さくらサーバーのMySQLへの接続情報が正確か確認してください。

### 時間表示の問題
- フロントエンドとバックエンドの間で時間のフォーマットが一致しているか確認してください。
- タイムゾーンの設定が正しいか確認してください。

## 定期的なメンテナンス

1. 定期的なバックアップの実行
```bash
# cronに登録して毎日実行するなど
0 3 * * * cd /path/to/app/cgi-bin/requestForm_api && bash backup_db.sh
```

2. 古いバックアップの削除
バックアップスクリプトは30日以上経過したバックアップファイルを自動的に削除します。

## ライセンス
このプロジェクトは内部利用を目的としており、無断での複製・配布は禁止されています。
