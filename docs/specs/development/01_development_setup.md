# 開発環境構築手順書 - 要望管理システム

## ドキュメント情報

| 項目 | 内容 |
|------|------|
| ドキュメント名 | 開発環境構築手順書 |
| システム名 | 電子カルテシステム要望管理システム |
| バージョン | 1.0 |
| 作成日 | 2026-01-05 |
| 最終更新日 | 2026-01-05 |
| ステータス | 引き渡し版 |

## 目次

1. [前提条件](#1-前提条件)
2. [プロジェクトの取得](#2-プロジェクトの取得)
3. [バックエンド環境構築](#3-バックエンド環境構築)
4. [フロントエンド環境構築](#4-フロントエンド環境構築)
5. [データベースセットアップ](#5-データベースセットアップ)
6. [開発サーバーの起動](#6-開発サーバーの起動)
7. [開発ツールの設定](#7-開発ツールの設定)
8. [トラブルシューティング](#8-トラブルシューティング)

---

## 1. 前提条件

### 1.1 必要なソフトウェア

開発を開始する前に、以下のソフトウェアをインストールしてください。

| ソフトウェア | バージョン | 用途 | ダウンロードURL |
|------------|-----------|------|---------------|
| **Node.js** | 18.x 以上 | フロントエンド開発環境 | https://nodejs.org/ |
| **npm** | 9.x 以上 | フロントエンド パッケージ管理 | Node.js に付属 |
| **Python** | 3.8 以上 | バックエンド開発環境 | https://www.python.org/ |
| **pip** | 最新版 | バックエンド パッケージ管理 | Python に付属 |
| **Git** | 2.x 以上 | バージョン管理 | https://git-scm.com/ |
| **VSCode** | 最新版 | 推奨エディタ（任意） | https://code.visualstudio.com/ |
| **MySQL** | 5.7+ または 8.x | 本番同等環境（任意） | https://dev.mysql.com/downloads/ |

### 1.2 バージョン確認コマンド

インストール後、以下のコマンドでバージョンを確認してください。

```bash
# Node.js バージョン確認
node --version
# 出力例: v18.17.0

# npm バージョン確認
npm --version
# 出力例: 9.6.7

# Python バージョン確認
python3 --version
# 出力例: Python 3.11.4

# pip バージョン確認
pip3 --version
# 出力例: pip 23.1.2

# Git バージョン確認
git --version
# 出力例: git version 2.40.0
```

### 1.3 推奨スペック

| 項目 | 推奨値 |
|------|--------|
| CPU | 2コア以上 |
| メモリ | 8GB以上 |
| ディスク空き容量 | 5GB以上 |
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ |

---

## 2. プロジェクトの取得

### 2.1 GitHubからクローン

```bash
# 任意の作業ディレクトリへ移動
cd ~/Development

# リポジトリをクローン
git clone https://github.com/keinomura/requestForm.git

# プロジェクトディレクトリへ移動
cd requestForm

# ブランチ確認
git branch
# * main

# ファイル構造確認
ls -la
```

**期待されるディレクトリ構造**:
```
requestForm/
├── README.md
├── frontend/           # Vue.js フロントエンド
├── cgi-bin/           # Flask バックエンド
│   └── requestForm_api/
└── docs/              # ドキュメント（今回作成）
```

### 2.2 SSH接続設定（GitHub）

**HTTPSでのクローンで問題ない場合はスキップ可**

```bash
# SSH鍵生成（未作成の場合）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 公開鍵をクリップボードにコピー（macOS）
pbcopy < ~/.ssh/id_ed25519.pub

# または cat で表示してコピー
cat ~/.ssh/id_ed25519.pub

# GitHubに公開鍵を登録
# https://github.com/settings/keys
# "New SSH key" をクリックして公開鍵を貼り付け
```

---

## 3. バックエンド環境構築

### 3.1 Python仮想環境の作成

```bash
# バックエンドディレクトリへ移動
cd cgi-bin/requestForm_api

# 仮想環境を作成
python3 -m venv venv

# 仮想環境をアクティベート
# macOS/Linux:
source venv/bin/activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (cmd):
venv\Scripts\activate.bat

# アクティベート成功の確認（プロンプトに (venv) が表示される）
# (venv) user@machine:~/requestForm/cgi-bin/requestForm_api$
```

### 3.2 依存パッケージのインストール

```bash
# 仮想環境がアクティベートされていることを確認
# (venv) が表示されているか確認

# 依存パッケージをインストール
pip install -r requirements.txt

# インストール確認
pip list
# Flask
# Flask-SQLAlchemy
# Flask-CORS
# PyMySQL
# などが表示されることを確認
```

**requirements.txt の内容**:
```
Flask
Flask-SQLAlchemy
Flask-CORS
PyMySQL
```

### 3.3 環境変数の設定

```bash
# .env ファイルを作成（開発環境用）
cat > .env << 'EOF'
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///../request_management.db
API_PREFIX=/
EOF

# .env ファイルの確認
cat .env
```

**設定内容の説明**:

| 変数名 | 値 | 説明 |
|-------|---|------|
| FLASK_ENV | development | 開発モードで実行 |
| FLASK_DEBUG | 1 | デバッグモード有効（エラー詳細表示） |
| DATABASE_URL | sqlite:///../request_management.db | SQLiteを使用（開発用） |
| API_PREFIX | / | APIのベースパス |

---

### 3.4 データベースの初期化

```bash
# Pythonインタラクティブシェルを起動
python3

# 以下を実行
>>> from app import db
>>> db.create_all()
>>> exit()

# データベースファイルが作成されたことを確認
ls -la request_management.db
# -rw-r--r-- 1 user staff 12288 Jan  5 14:30 request_management.db
```

**SQLiteデータベースの場所**: `cgi-bin/request_management.db`

---

### 3.5 開発用サンプルデータの投入（任意）

```bash
# Pythonインタラクティブシェルを起動
python3

# 以下を実行してサンプルデータを投入
>>> from app import db, Request, Response
>>> import uuid
>>> from datetime import datetime

# サンプル要望を作成
>>> req1 = Request(
...     request_uuid=str(uuid.uuid4()),
...     content='ログイン画面の改善要望',
...     requester_department='内科',
...     requester_name='山田太郎',
...     status='未対応'
... )
>>> db.session.add(req1)

>>> req2 = Request(
...     request_uuid=str(uuid.uuid4()),
...     content='患者検索機能の追加希望',
...     requester_department='外科',
...     requester_name='佐藤花子',
...     status='覚知(対応中)'
... )
>>> db.session.add(req2)

>>> db.session.commit()
>>> exit()
```

---

### 3.6 バックエンドサーバーの起動テスト

```bash
# 仮想環境がアクティベートされていることを確認
# (venv) が表示されているか確認

# Flask開発サーバーを起動
python3 app.py

# 以下のようなメッセージが表示される
# * Running on http://127.0.0.1:5000
# * Restarting with stat
# * Debugger is active!
```

**別のターミナルで動作確認**:

```bash
# API エンドポイントにアクセス
curl http://127.0.0.1:5000/requests

# JSON形式で要望一覧が返却されることを確認
# [{"request_uuid":"...","content":"..."}]
```

**サーバーの停止**: `Ctrl + C`

---

## 4. フロントエンド環境構築

### 4.1 Node.js 依存パッケージのインストール

```bash
# フロントエンドディレクトリへ移動
cd ../../frontend

# package.jsonの存在確認
ls -la package.json

# 依存パッケージをインストール
npm install

# インストール完了までしばらく待つ（1〜3分程度）
# node_modules/ ディレクトリが作成される
```

**主要パッケージ**:
- vue: 3.5.12
- vuetify: 3.7.4
- vue-router: 4.4.5
- axios: 1.7.7
- vite: 5.4.10

### 4.2 環境変数の設定

```bash
# .env.development ファイルを作成
cat > .env.development << 'EOF'
VITE_API_URL=http://127.0.0.1:5000
VITE_BASE_URL=/
EOF

# ファイルの確認
cat .env.development
```

**設定内容の説明**:

| 変数名 | 値 | 説明 |
|-------|---|------|
| VITE_API_URL | http://127.0.0.1:5000 | バックエンドAPIのURL |
| VITE_BASE_URL | / | フロントエンドのベースURL |

---

### 4.3 フロントエンド開発サーバーの起動テスト

```bash
# 開発サーバーを起動
npm run dev

# 以下のようなメッセージが表示される
#   VITE v5.4.10  ready in 500 ms
#
#   ➜  Local:   http://localhost:5173/
#   ➜  Network: use --host to expose
#   ➜  press h + enter to show help
```

**ブラウザでアクセス**:
- URL: http://localhost:5173/
- 要望一覧画面が表示されることを確認

**サーバーの停止**: `Ctrl + C`

---

## 5. データベースセットアップ

### 5.1 開発環境（SQLite）

**デフォルトで使用**: 上記の手順で既にセットアップ済み

**データベースファイル**: `cgi-bin/request_management.db`

**接続方法**:
```bash
# SQLiteコマンドラインツール
sqlite3 cgi-bin/request_management.db

# テーブル一覧確認
.tables
# Requests  Responses

# レコード確認
SELECT * FROM Requests;

# 終了
.exit
```

---

### 5.2 本番同等環境（MySQL）の構築（任意）

**ローカルでMySQLを使いたい場合**:

#### 5.2.1 MySQLのインストール

**macOS (Homebrew)**:
```bash
brew install mysql
brew services start mysql
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

**Windows**:
- MySQL Installer からインストール
- https://dev.mysql.com/downloads/installer/

---

#### 5.2.2 データベースとユーザーの作成

```bash
# MySQLに接続
mysql -u root -p

# データベース作成
CREATE DATABASE requestform_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# ユーザー作成と権限付与
CREATE USER 'requestform_user'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON requestform_dev.* TO 'requestform_user'@'localhost';
FLUSH PRIVILEGES;

# 終了
EXIT;
```

---

#### 5.2.3 バックエンドの設定変更

```bash
cd cgi-bin/requestForm_api

# .env ファイルを編集
cat > .env << 'EOF'
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=mysql+pymysql://requestform_user:dev_password@localhost/requestform_dev
API_PREFIX=/
EOF
```

#### 5.2.4 テーブル作成

```bash
# 仮想環境をアクティベート
source venv/bin/activate

# Pythonインタラクティブシェル
python3

>>> from app import db
>>> db.create_all()
>>> exit()
```

---

## 6. 開発サーバーの起動

### 6.1 バックエンドとフロントエンドの同時起動

**ターミナル1（バックエンド）**:

```bash
# バックエンドディレクトリへ移動
cd /path/to/requestForm/cgi-bin/requestForm_api

# 仮想環境をアクティベート
source venv/bin/activate

# Flask開発サーバー起動
python3 app.py

# 起動確認
# * Running on http://127.0.0.1:5000
```

**ターミナル2（フロントエンド）**:

```bash
# フロントエンドディレクトリへ移動
cd /path/to/requestForm/frontend

# Vite開発サーバー起動
npm run dev

# 起動確認
# ➜  Local:   http://localhost:5173/
```

---

### 6.2 動作確認

1. **ブラウザで http://localhost:5173/ にアクセス**
2. **要望一覧画面が表示されることを確認**
3. **「要望登録」ボタンをクリック**
4. **新規要望を登録してみる**:
   - 要望内容: "テスト要望"
   - 部署: "開発部"
   - 氏名: "テストユーザー"
   - 「登録」ボタンをクリック
5. **要望一覧に表示されることを確認**

---

### 6.3 ホットリロード（開発中の自動反映）

**フロントエンド**:
- Vue.jsファイル（`.vue`, `.js`）を編集すると自動的にブラウザが更新される

**バックエンド**:
- `app.py` を編集すると自動的にFlaskサーバーが再起動される
- `FLASK_DEBUG=1` の設定により有効化

---

## 7. 開発ツールの設定

### 7.1 VSCodeの推奨設定

#### 7.1.1 推奨拡張機能

**拡張機能のインストール**:

1. VSCodeを起動
2. 左サイドバーの「拡張機能」アイコンをクリック
3. 以下の拡張機能を検索してインストール

| 拡張機能名 | ID | 用途 |
|-----------|-----|------|
| Volar | Vue.volar | Vue 3 サポート |
| ESLint | dbaeumer.vscode-eslint | JavaScriptリンター |
| Prettier | esbenp.prettier-vscode | コードフォーマッター |
| Python | ms-python.python | Python開発サポート |
| Pylance | ms-python.vscode-pylance | Python言語サーバー |

#### 7.1.2 ワークスペース設定

**`.vscode/settings.json` を作成**:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "vue"
  ],
  "files.associations": {
    "*.vue": "vue"
  }
}
```

---

### 7.2 Git設定

#### 7.2.1 .gitignore の確認

プロジェクトルートの `.gitignore` が以下を含むことを確認:

```
# 依存関係
node_modules/
venv/
__pycache__/

# 環境変数
.env
.env_for_mySQL

# データベース
*.db
*.sqlite

# ビルド成果物
dist/
*.pyc

# IDE
.vscode/
.idea/

# ログ
*.log

# バックアップ
backups/
```

#### 7.2.2 Git初期設定

```bash
# ユーザー名とメールアドレスを設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# デフォルトブランチ名を main に設定
git config --global init.defaultBranch main

# エディタ設定（例: VSCode）
git config --global core.editor "code --wait"
```

---

### 7.3 デバッグ設定

#### 7.3.1 VSCode デバッグ設定（バックエンド）

**`.vscode/launch.json` を作成**:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "app.py",
        "FLASK_ENV": "development",
        "FLASK_DEBUG": "1"
      },
      "args": [
        "run",
        "--no-debugger",
        "--no-reload"
      ],
      "jinja": true,
      "cwd": "${workspaceFolder}/cgi-bin/requestForm_api"
    }
  ]
}
```

**使い方**:
1. VSCodeのデバッグパネルを開く（Ctrl+Shift+D / Cmd+Shift+D）
2. "Python: Flask" を選択
3. F5キーでデバッグ開始
4. ブレークポイントを設定して動作確認

---

#### 7.3.2 ブラウザ開発者ツール（フロントエンド）

**Chrome DevTools**:

1. ブラウザで http://localhost:5173/ を開く
2. F12キーを押して開発者ツールを開く
3. **Console**: JavaScriptエラー確認
4. **Network**: API通信確認
5. **Vue DevTools**: Vue.js専用デバッグツール（拡張機能のインストールが必要）

**Vue DevTools のインストール**:
- Chrome Web Store で "Vue.js devtools" を検索してインストール
- https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd

---

## 8. トラブルシューティング

### 8.1 よくある問題と解決方法

#### 8.1.1 npm install が失敗する

**症状**: `npm install` 実行時にエラー

**原因**:
- Node.jsのバージョンが古い
- package-lock.json の破損

**解決方法**:

```bash
# Node.jsバージョン確認
node --version
# 18.x 未満の場合はアップデート

# package-lock.json と node_modules を削除
rm -rf node_modules package-lock.json

# 再インストール
npm install
```

---

#### 8.1.2 Flask サーバーが起動しない

**症状**: `python3 app.py` 実行時にエラー

**原因**:
- 仮想環境がアクティベートされていない
- 依存パッケージがインストールされていない
- ポート5000が使用中

**解決方法**:

```bash
# 仮想環境の確認
which python3
# 仮想環境のパスが表示されない場合はアクティベート
source venv/bin/activate

# 依存パッケージの再インストール
pip install -r requirements.txt

# ポート確認（macOS/Linux）
lsof -i :5000
# 使用中の場合はプロセスを終了
kill -9 [PID]
```

---

#### 8.1.3 API通信エラー（CORSエラー）

**症状**: ブラウザコンソールに `CORS policy` エラー

**原因**:
- Flask-CORSが正しく設定されていない
- バックエンドサーバーが起動していない

**解決方法**:

```bash
# バックエンドが起動しているか確認
curl http://127.0.0.1:5000/requests

# Flask-CORSがインストールされているか確認
pip list | grep Flask-CORS

# インストールされていない場合
pip install Flask-CORS

# app.py の確認
grep "CORS" cgi-bin/requestForm_api/app.py
# CORS(app) が記述されていることを確認
```

---

#### 8.1.4 データベース接続エラー

**症状**: `SQLAlchemy` 関連のエラー

**原因**:
- DATABASE_URL が正しくない
- データベースファイルが存在しない（SQLiteの場合）
- MySQLサーバーが起動していない（MySQLの場合）

**解決方法**:

**SQLiteの場合**:
```bash
# .env ファイルの確認
cat .env | grep DATABASE_URL
# sqlite:///../request_management.db になっているか確認

# データベースファイルの再作成
python3
>>> from app import db
>>> db.create_all()
>>> exit()
```

**MySQLの場合**:
```bash
# MySQLサーバーの起動確認
mysql -u requestform_user -p -e "SHOW DATABASES;"

# 接続できない場合はMySQLを起動
# macOS (Homebrew):
brew services start mysql

# Ubuntu/Debian:
sudo systemctl start mysql
```

---

#### 8.1.5 Vue.jsコンポーネントが表示されない

**症状**: ブラウザに何も表示されない、または真っ白

**原因**:
- JavaScriptエラー
- API URLが間違っている
- ビルドエラー

**解決方法**:

```bash
# ブラウザコンソールでエラー確認（F12 → Console）

# .env.development の確認
cat frontend/.env.development
# VITE_API_URL が正しいか確認

# Vite開発サーバーを再起動
# Ctrl+C で停止後、再度起動
npm run dev

# キャッシュクリア
rm -rf frontend/node_modules/.vite
npm run dev
```

---

#### 8.1.6 Python仮想環境がアクティベートできない

**症状**: `source venv/bin/activate` でエラー

**原因**:
- 仮想環境が正しく作成されていない
- スクリプト実行権限がない

**解決方法**:

```bash
# 仮想環境の再作成
rm -rf venv
python3 -m venv venv

# アクティベート
source venv/bin/activate

# Windows PowerShellの場合、実行ポリシーを変更
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

---

### 8.2 デバッグのヒント

#### 8.2.1 バックエンドのデバッグ

**print文でのデバッグ**:
```python
# app.py に追加
@app.route('/requests', methods=['GET'])
def get_requests():
    print('=== get_requests called ===')  # デバッグ出力
    requests = Request.query.all()
    print(f'Found {len(requests)} requests')  # デバッグ出力
    return jsonify([req.to_dict() for req in requests])
```

**ブレークポイントでのデバッグ**:
```python
# app.py に追加
import pdb

@app.route('/requests', methods=['POST'])
def create_request():
    pdb.set_trace()  # ここで処理が止まる
    data = request.json
    # ...
```

---

#### 8.2.2 フロントエンドのデバッグ

**console.log でのデバッグ**:
```javascript
// RequestList.vue
async fetchRequests() {
  console.log('=== fetchRequests called ===')  // デバッグ出力
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/requests`)
    console.log('API response:', response.data)  // デバッグ出力
    this.requests = response.data
  } catch (error) {
    console.error('API error:', error)  // エラー出力
  }
}
```

**Vue DevTools でのデバッグ**:
1. ブラウザでVue DevToolsを開く
2. "Components" タブでコンポーネントツリーを確認
3. データやpropsの値を確認
4. Stateの変更を追跡

---

## 9. 次のステップ

### 9.1 開発ワークフロー

1. **機能追加・バグ修正**:
```bash
# 新しいブランチを作成
git checkout -b feature/new-feature

# コード編集

# テスト

# コミット
git add .
git commit -m "Add new feature"

# プッシュ
git push origin feature/new-feature

# GitHub でプルリクエスト作成
```

2. **コードレビュー**:
   - プルリクエストを他の開発者にレビュー依頼
   - フィードバックに基づいて修正

3. **マージ**:
   - レビュー承認後、mainブランチにマージ

---

### 9.2 推奨学習リソース

#### フロントエンド

| 技術 | 公式ドキュメント |
|------|---------------|
| Vue.js 3 | https://vuejs.org/ |
| Vuetify 3 | https://vuetifyjs.com/ |
| Vue Router | https://router.vuejs.org/ |
| Axios | https://axios-http.com/ |

#### バックエンド

| 技術 | 公式ドキュメント |
|------|---------------|
| Flask | https://flask.palletsprojects.com/ |
| Flask-SQLAlchemy | https://flask-sqlalchemy.palletsprojects.com/ |
| SQLAlchemy | https://www.sqlalchemy.org/ |

---

### 9.3 開発規約

#### コーディング規約

**Python (PEP 8)**:
- インデント: スペース4つ
- 行の長さ: 最大79文字
- 関数名: `snake_case`
- クラス名: `PascalCase`

**JavaScript (ESLint + Prettier)**:
- インデント: スペース2つ
- セミコロン: あり
- シングルクォート優先
- 末尾カンマ: あり

**Vue.js**:
- コンポーネント名: `PascalCase`
- ファイル名: `PascalCase.vue`
- props: `camelCase`
- イベント: `kebab-case`

---

#### Git コミットメッセージ

**フォーマット**:
```
<type>: <subject>

<body>
```

**type の種類**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更
- `style`: コードスタイル変更（機能変更なし）
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルドプロセスやツール変更

**例**:
```
feat: Add request search functionality

- Add search filters for department and name
- Implement date range search
- Update UI with search form component
```

---

## 10. チェックリスト

### 10.1 初回セットアップ完了チェックリスト

環境構築が完了したら、以下を確認してください。

- [ ] Node.js と npm がインストールされている
- [ ] Python 3.8+ と pip がインストールされている
- [ ] Git がインストールされている
- [ ] プロジェクトをGitHubからクローン済み
- [ ] バックエンド仮想環境が作成されている
- [ ] バックエンド依存パッケージがインストール済み
- [ ] バックエンド .env ファイルが設定済み
- [ ] データベースが初期化されている
- [ ] フロントエンド依存パッケージがインストール済み
- [ ] フロントエンド .env.development ファイルが設定済み
- [ ] バックエンドサーバーが起動できる（http://127.0.0.1:5000）
- [ ] フロントエンドサーバーが起動できる（http://localhost:5173）
- [ ] ブラウザで要望一覧画面が表示される
- [ ] 新規要望が登録できる
- [ ] 要望の更新ができる
- [ ] VSCode の推奨拡張機能がインストール済み（任意）

---

## 11. サポート・問い合わせ

### 11.1 ドキュメント

- [システム仕様書](../system/01_system_overview.md)
- [技術仕様書](../technical/01_technical_architecture.md)
- [運用マニュアル](../operations/01_operations_manual.md)
- [README.md](../../../README.md)

### 11.2 リポジトリ

- **GitHub**: https://github.com/keinomura/requestForm.git
- **Issues**: https://github.com/keinomura/requestForm/issues

### 11.3 連絡先

| 項目 | 連絡先 |
|------|--------|
| プロジェクト担当 | [担当者名] / [連絡先] |
| SE部 | [電話番号] / [メールアドレス] |

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|---------|--------|
| 1.0 | 2026-01-05 | 初版作成（引き渡し版） | - |

---

**以上**
