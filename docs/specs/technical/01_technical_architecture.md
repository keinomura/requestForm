# 技術仕様書 - 要望管理システム

## ドキュメント情報

| 項目 | 内容 |
|------|------|
| ドキュメント名 | 技術仕様書 |
| システム名 | 電子カルテシステム要望管理システム |
| バージョン | 1.0 |
| 作成日 | 2026-01-05 |
| 最終更新日 | 2026-01-05 |
| ステータス | 引き渡し版 |

## 目次

1. [システムアーキテクチャ](#1-システムアーキテクチャ)
2. [技術スタック](#2-技術スタック)
3. [データベース設計](#3-データベース設計)
4. [API仕様](#4-api仕様)
5. [フロントエンド設計](#5-フロントエンド設計)
6. [バックエンド設計](#6-バックエンド設計)
7. [デプロイメント構成](#7-デプロイメント構成)
8. [セキュリティ設計](#8-セキュリティ設計)

---

## 1. システムアーキテクチャ

### 1.1 全体アーキテクチャ

```
[クライアント層]
    ↓ HTTPS
[Webサーバー層]
    ↓
[アプリケーション層]
    ↓
[データベース層]
```

### 1.2 アーキテクチャ詳細図

```
┌─────────────────────────────────────────────────────────┐
│ クライアント                                             │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│ │ PC       │  │ Tablet   │  │ Mobile   │              │
│ │ Browser  │  │ Browser  │  │ Browser  │              │
│ └──────────┘  └──────────┘  └──────────┘              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS (443)
┌────────────────────┴────────────────────────────────────┐
│ Webサーバー (Sakura Internet)                            │
│ felddorf.sakura.ne.jp                                   │
│                                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ 静的ファイル配信                                    │ │
│ │ ~/www/requestForm/                                 │ │
│ │ - index.html                                       │ │
│ │ - assets/                                          │ │
│ │   - JavaScript bundles                             │ │
│ │   - CSS files                                      │ │
│ └────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ CGI実行環境                                         │ │
│ │ ~/www/cgi-bin/                                     │ │
│ │                                                     │ │
│ │ index.cgi ─→ requestForm_api/app.py (Flask)        │ │
│ │              ↓                                      │ │
│ │              venv/ (Python仮想環境)                │ │
│ └────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ MySQL Protocol
┌────────────────────┴────────────────────────────────────┐
│ データベースサーバー (Sakura Internet)                   │
│ [MySQLホスト名]                               │
│                                                          │
│ ┌────────────────────────────────────────────────────┐ │
│ │ MySQL 5.7+                                         │ │
│ │ Database: [データベース名]                      │ │
│ │                                                     │ │
│ │ ┌──────────┐  ┌──────────┐                        │ │
│ │ │Requests  │  │Responses │                        │ │
│ │ └──────────┘  └──────────┘                        │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 1.3 通信フロー

1. **静的ファイル配信**:
   - `https://felddorf.sakura.ne.jp/requestForm/` → Vue.js SPA (index.html)
   - ブラウザがJavaScript/CSSをロード

2. **API通信**:
   - Vue.js → `https://felddorf.sakura.ne.jp/requestForm_api/*` → Flask API
   - Flask → MySQL Database

3. **データフロー**:
   - クライアント → JSON over HTTPS → Flask API → SQLAlchemy → MySQL

---

## 2. 技術スタック

### 2.1 フロントエンド

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| **フレームワーク** | Vue.js | 3.5.12 | UIフレームワーク |
| **ルーティング** | Vue Router | 4.4.5 | SPA ルーティング |
| **UIライブラリ** | Vuetify | 3.7.4 | Material Design コンポーネント |
| **ビルドツール** | Vite | 5.4.10 | 開発サーバー・ビルド |
| **HTTP クライアント** | Axios | 1.7.7 | API通信 |
| **リンター** | ESLint | 9.14.0 | コード品質管理 |
| **フォーマッター** | Prettier | 3.3.3 | コード整形 |
| **アイコン** | MDI | 7.4.47 | Material Design Icons |

#### 主要プラグイン・ライブラリ

```json
{
  "@mdi/font": "^7.4.47",
  "@vitejs/plugin-vue": "^5.1.4",
  "eslint-plugin-vue": "^9.29.1",
  "roboto-fontface": "*",
  "vite-plugin-vuetify": "^2.0.4"
}
```

### 2.2 バックエンド

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| **言語** | Python | 3.x | サーバーサイド言語 |
| **フレームワーク** | Flask | latest | Web API フレームワーク |
| **ORM** | Flask-SQLAlchemy | - | データベースORM |
| **CORS** | Flask-CORS | - | クロスオリジン対応 |
| **DBドライバ** | PyMySQL | - | MySQL接続ドライバ |
| **本番DB** | MySQL | 5.7+ | 本番データベース |
| **開発DB** | SQLite | 3.x | 開発用データベース |

#### 依存パッケージ ([requirements.txt](../../../cgi-bin/requestForm_api/requirements.txt))

```
Flask
Flask-SQLAlchemy
Flask-CORS
PyMySQL
```

### 2.3 インフラストラクチャ

| カテゴリ | 技術 | 詳細 |
|---------|------|------|
| **ホスティング** | さくらインターネット レンタルサーバー | https://felddorf.sakura.ne.jp |
| **Webサーバー** | Apache (CGI) | さくらレンタルサーバー標準 |
| **データベース** | MySQL | さくらレンタルサーバー提供 |
| **バージョン管理** | Git / GitHub | https://github.com/keinomura/requestForm.git |

### 2.4 開発ツール

| ツール | 用途 |
|-------|------|
| npm | フロントエンド パッケージ管理 |
| pip | バックエンド パッケージ管理 |
| venv | Python 仮想環境 |
| Git | バージョン管理 |

---

## 3. データベース設計

### 3.1 ER図

```
┌─────────────────────────────────┐
│ Requests                        │
├─────────────────────────────────┤
│ PK  request_uuid (VARCHAR 36)   │
│     content (TEXT)               │
│     requester_department (VARCHAR 255) │
│     requester_name (VARCHAR 255)│
│     input_date (DATETIME)       │
│     status (VARCHAR 50)         │
│     response_comment (TEXT)     │
│     assigned_department (VARCHAR 255)  │
│     assigned_person (VARCHAR 255)│
│     update_date (DATETIME)      │
└──────────┬──────────────────────┘
           │ 1
           │
           │ N
┌──────────┴──────────────────────┐
│ Responses                       │
├─────────────────────────────────┤
│ PK  response_uuid (VARCHAR 36)  │
│ FK  request_uuid (VARCHAR 36)   │
│     handler_company (VARCHAR 255)│
│     handler_department (VARCHAR 255) │
│     handler_name (VARCHAR 255)  │
│     status (VARCHAR 50)         │
│     response_comment (TEXT)     │
│     final_response (TEXT)       │
│     response_date (DATETIME)    │
│     final_response_date (DATETIME)│
└─────────────────────────────────┘
```

### 3.2 テーブル定義

#### 3.2.1 Requests（要望テーブル）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| request_uuid | VARCHAR(36) | NO | - | PRIMARY KEY | 要望の一意識別子（UUID） |
| content | TEXT | NO | - | - | 要望の内容 |
| requester_department | VARCHAR(255) | YES | NULL | - | 要望者の所属部署 |
| requester_name | VARCHAR(255) | YES | NULL | - | 要望者の氏名 |
| input_date | DATETIME | NO | CURRENT_TIMESTAMP | - | 要望の登録日時（UTC） |
| status | VARCHAR(50) | NO | '未対応' | - | 要望の現在のステータス |
| response_comment | TEXT | YES | NULL | - | 最新の対応コメント |
| assigned_department | VARCHAR(255) | YES | NULL | - | 担当部署 |
| assigned_person | VARCHAR(255) | YES | NULL | - | 担当者氏名 |
| update_date | DATETIME | NO | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | 最終更新日時（UTC） |

**インデックス**:
- PRIMARY KEY: `request_uuid`
- 推奨: `status`, `update_date`, `input_date`

**CREATE TABLE文**:
```sql
CREATE TABLE Requests (
    request_uuid VARCHAR(36) PRIMARY KEY,
    content TEXT NOT NULL,
    requester_department VARCHAR(255),
    requester_name VARCHAR(255),
    input_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT '未対応',
    response_comment TEXT,
    assigned_department VARCHAR(255),
    assigned_person VARCHAR(255),
    update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 3.2.2 Responses（対応履歴テーブル）

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---------|---------|------|-----------|------|------|
| response_uuid | VARCHAR(36) | NO | - | PRIMARY KEY | 対応履歴の一意識別子（UUID） |
| request_uuid | VARCHAR(36) | NO | - | FOREIGN KEY | 紐づく要望のUUID |
| handler_company | VARCHAR(255) | YES | NULL | - | 対応企業・システム名 |
| handler_department | VARCHAR(255) | YES | NULL | - | 対応部署 |
| handler_name | VARCHAR(255) | YES | NULL | - | 対応者氏名 |
| status | VARCHAR(50) | NO | '未対応' | - | 対応時点のステータス |
| response_comment | TEXT | YES | NULL | - | 対応コメント |
| final_response | TEXT | YES | NULL | - | 最終対応内容 |
| response_date | DATETIME | NO | CURRENT_TIMESTAMP | - | 対応日時（UTC） |
| final_response_date | DATETIME | YES | NULL | - | 最終対応日時（UTC） |

**インデックス**:
- PRIMARY KEY: `response_uuid`
- FOREIGN KEY: `request_uuid` REFERENCES Requests(request_uuid) ON DELETE CASCADE
- 推奨: `request_uuid`, `response_date`

**CREATE TABLE文**:
```sql
CREATE TABLE Responses (
    response_uuid VARCHAR(36) PRIMARY KEY,
    request_uuid VARCHAR(36) NOT NULL,
    handler_company VARCHAR(255),
    handler_department VARCHAR(255),
    handler_name VARCHAR(255),
    status VARCHAR(50) DEFAULT '未対応',
    response_comment TEXT,
    final_response TEXT,
    response_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    final_response_date DATETIME,
    FOREIGN KEY (request_uuid) REFERENCES Requests(request_uuid) ON DELETE CASCADE
);
```

### 3.3 マスターデータ

#### 3.3.1 ステータス値

```python
# アプリケーション内で定義
STATUS_OPTIONS = [
    '未対応',
    '覚知(対応検討中)',
    '覚知(対応中)',
    '要病院対応',
    '一時対応完了(要作業)',
    '対応完了(承認前)',
    '対応完了(電カル委員会承認)',  # 管理者専用
    '要追加情報',
    '対応保留',
    '対応不可'
]
```

#### 3.3.2 対応企業・システム

```python
HANDLER_COMPANIES = [
    '電子カルテシステム',
    'ネットワークシステム',
    '画像システム',
    'その他'
]
```

### 3.4 データベース移行

#### マイグレーション履歴

| ファイル名 | 実施日 | 内容 |
|-----------|--------|------|
| migration_add_handler_company.json | 2025-05-15 | Responsesテーブルにhandler_companyカラム追加 |

#### マイグレーション実施方法

```bash
cd cgi-bin/requestForm_api
python db_migration.py --apply migrations/migration_add_handler_company.json
```

---

## 4. API仕様

### 4.1 API エンドポイント一覧

**ベースURL**:
- 開発: `http://127.0.0.1:5000`
- 本番: `https://felddorf.sakura.ne.jp/requestForm_api`

#### 4.1.1 要望管理API

| メソッド | エンドポイント | 説明 | 認証 |
|---------|--------------|------|------|
| GET | `/requests` | 全要望取得 | - |
| POST | `/requests` | 新規要望登録 | - |
| PUT | `/requests/<uuid>` | 要望更新 | - |
| DELETE | `/requests/<uuid>` | 要望削除 | - |
| GET | `/requests/<uuid>/comments` | 要望のコメント履歴取得 | - |

#### 4.1.2 対応履歴API

| メソッド | エンドポイント | 説明 | 認証 |
|---------|--------------|------|------|
| POST | `/responses` | 対応コメント追加 | - |
| DELETE | `/comments/<uuid>` | コメント削除 | - |

### 4.2 API 詳細仕様

#### 4.2.1 GET /requests

**説明**: 登録されているすべての要望を取得

**リクエスト**:
```
GET /requests HTTP/1.1
Host: felddorf.sakura.ne.jp
```

**レスポンス** (Success: 200 OK):
```json
[
  {
    "request_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "content": "ログイン画面の改善要望",
    "requester_department": "内科",
    "requester_name": "山田太郎",
    "input_date": "2026-01-05T05:30:00",
    "status": "覚知(対応中)",
    "response_comment": "対応を開始しました",
    "assigned_department": "SE部",
    "assigned_person": "佐藤花子",
    "update_date": "2026-01-05T06:00:00"
  },
  ...
]
```

**レスポンスフィールド**:
- すべての日時はUTC形式で返却
- フロントエンド側でJST変換を実施

---

#### 4.2.2 POST /requests

**説明**: 新規要望を登録

**リクエスト**:
```json
POST /requests HTTP/1.1
Host: felddorf.sakura.ne.jp
Content-Type: application/json

{
  "content": "患者検索機能の改善希望",
  "requester_department": "外科",
  "requester_name": "鈴木一郎"
}
```

**リクエストボディ**:
| フィールド | 型 | 必須 | 説明 |
|-----------|-----|-----|------|
| content | string | ○ | 要望内容 |
| requester_department | string | - | 要望者の所属部署 |
| requester_name | string | - | 要望者氏名 |

**レスポンス** (Success: 201 Created):
```json
{
  "message": "Request created successfully",
  "request_uuid": "650e8400-e29b-41d4-a716-446655440001"
}
```

**エラーレスポンス** (400 Bad Request):
```json
{
  "error": "Content is required"
}
```

---

#### 4.2.3 PUT /requests/<uuid>

**説明**: 既存要望の情報を更新（ステータス、担当者など）

**リクエスト**:
```json
PUT /requests/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: felddorf.sakura.ne.jp
Content-Type: application/json

{
  "status": "覚知(対応中)",
  "response_comment": "対応を開始しました",
  "handler_company": "電子カルテシステム",
  "assigned_department": "SE部",
  "assigned_person": "佐藤花子"
}
```

**リクエストボディ**:
| フィールド | 型 | 必須 | 説明 |
|-----------|-----|-----|------|
| status | string | - | ステータス |
| response_comment | string | - | 対応コメント |
| handler_company | string | - | 対応企業・システム |
| assigned_department | string | - | 担当部署 |
| assigned_person | string | - | 担当者氏名 |

**レスポンス** (Success: 200 OK):
```json
{
  "message": "Request updated successfully"
}
```

**エラーレスポンス** (404 Not Found):
```json
{
  "error": "Request not found"
}
```

---

#### 4.2.4 DELETE /requests/<uuid>

**説明**: 要望を削除（関連するコメントも連鎖削除）

**リクエスト**:
```
DELETE /requests/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: felddorf.sakura.ne.jp
```

**レスポンス** (Success: 200 OK):
```json
{
  "message": "Request deleted successfully"
}
```

**エラーレスポンス** (404 Not Found):
```json
{
  "error": "Request not found"
}
```

---

#### 4.2.5 GET /requests/<uuid>/comments

**説明**: 特定要望の全コメント履歴を取得

**リクエスト**:
```
GET /requests/550e8400-e29b-41d4-a716-446655440000/comments HTTP/1.1
Host: felddorf.sakura.ne.jp
```

**レスポンス** (Success: 200 OK):
```json
[
  {
    "response_uuid": "750e8400-e29b-41d4-a716-446655440002",
    "request_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "handler_company": "電子カルテシステム",
    "handler_department": "SE部",
    "handler_name": "佐藤花子",
    "status": "覚知(対応中)",
    "response_comment": "対応を開始しました",
    "final_response": null,
    "response_date": "2026-01-05T06:00:00",
    "final_response_date": null
  },
  ...
]
```

---

#### 4.2.6 POST /responses

**説明**: 要望に対する対応コメントを追加

**リクエスト**:
```json
POST /responses HTTP/1.1
Host: felddorf.sakura.ne.jp
Content-Type: application/json

{
  "request_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "handler_company": "電子カルテシステム",
  "handler_department": "SE部",
  "handler_name": "佐藤花子",
  "status": "覚知(対応中)",
  "response_comment": "詳細を確認しています",
  "final_response": null,
  "response_date": "2026-01-05T07:00:00",
  "final_response_date": null
}
```

**リクエストボディ**:
| フィールド | 型 | 必須 | 説明 |
|-----------|-----|-----|------|
| request_uuid | string | ○ | 要望UUID |
| handler_company | string | - | 対応企業・システム |
| handler_department | string | - | 対応部署 |
| handler_name | string | - | 対応者氏名 |
| status | string | ○ | ステータス |
| response_comment | string | - | 対応コメント |
| final_response | string | - | 最終対応内容 |
| response_date | string | - | 対応日時（ISO 8601形式） |
| final_response_date | string | - | 最終対応日時（ISO 8601形式） |

**レスポンス** (Success: 201 Created):
```json
{
  "message": "Response created successfully",
  "response_uuid": "850e8400-e29b-41d4-a716-446655440003"
}
```

---

#### 4.2.7 DELETE /comments/<uuid>

**説明**: コメントを削除

**リクエスト**:
```
DELETE /comments/750e8400-e29b-41d4-a716-446655440002 HTTP/1.1
Host: felddorf.sakura.ne.jp
```

**レスポンス** (Success: 200 OK):
```json
{
  "message": "Comment deleted successfully"
}
```

**エラーレスポンス** (404 Not Found):
```json
{
  "error": "Comment not found"
}
```

---

### 4.3 CORS設定

Flask-CORSを使用してクロスオリジン通信を許可:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

**許可される通信**:
- Origin: すべて許可（本番環境では制限推奨）
- Methods: GET, POST, PUT, DELETE
- Headers: Content-Type, Authorization

---

## 5. フロントエンド設計

### 5.1 ディレクトリ構造

```
frontend/
├── public/                  # 静的ファイル
├── src/
│   ├── assets/             # 画像、フォントなど
│   ├── components/         # Vueコンポーネント
│   │   ├── AddRequest.vue
│   │   ├── RequestList.vue
│   │   └── UpdateProgress.vue (legacy)
│   ├── router/             # ルーティング設定
│   │   └── index.js
│   ├── views/              # ページビュー
│   ├── App.vue             # ルートコンポーネント
│   └── main.js             # エントリーポイント
├── .env.development        # 開発環境設定
├── .env.production         # 本番環境設定
├── vite.config.js          # Viteビルド設定
├── package.json            # 依存関係
└── dist/                   # ビルド成果物
```

### 5.2 コンポーネント設計

#### 5.2.1 App.vue（ルートコンポーネント）

**責務**:
- アプリケーション全体のレイアウト
- ヘッダー・ナビゲーション
- 管理者モード切替

**主要機能**:
```javascript
data() {
  return {
    isAdminMode: false  // 管理者モードフラグ
  }
}
```

**子コンポーネントへのprops**:
- `isAdminMode`: 管理者モード状態を各ページへ伝播

---

#### 5.2.2 RequestList.vue（要望一覧）

**責務**:
- 要望一覧表示
- 検索・フィルタリング
- 要望詳細表示（モーダル）
- 進捗更新（モーダル）
- 要望削除（管理者のみ）

**主要データ**:
```javascript
data() {
  return {
    requests: [],              // 要望一覧
    filteredRequests: [],      // フィルタ後の要望一覧
    searchFilters: {           // 検索条件
      content: '',
      department: '',
      name: '',
      status: '',
      dateFrom: null,
      dateTo: null
    },
    selectedRequest: null,     // 選択中の要望
    comments: [],              // コメント履歴
    showDetailDialog: false,   // 詳細ダイアログ表示フラグ
    showUpdateDialog: false,   // 更新ダイアログ表示フラグ
    updateForm: {              // 更新フォームデータ
      status: '',
      handlerCompany: '',
      assignedDepartment: '',
      assignedPerson: '',
      comment: '',
      password: ''
    }
  }
}
```

**主要メソッド**:
```javascript
methods: {
  async fetchRequests()        // 要望一覧取得
  searchRequests()             // 検索・フィルタ実行
  async viewDetails(request)   // 詳細表示
  openUpdateDialog(request)    // 更新ダイアログ表示
  async updateProgress()       // 進捗更新送信
  async deleteRequest(uuid)    // 要望削除
  async deleteComment(uuid)    // コメント削除
  getStatusColor(status)       // ステータスに応じた色取得
  getHandlerColor(company)     // 企業に応じた色取得
  formatDate(date)             // 日時フォーマット（UTC→JST）
}
```

**レスポンシブ対応**:
```javascript
computed: {
  isMobile() {
    return this.$vuetify.display.smAndDown  // 960px未満
  },
  isTablet() {
    return this.$vuetify.display.mdOnly     // 960px〜1279px
  },
  isDesktop() {
    return this.$vuetify.display.lgAndUp    // 1280px以上
  }
}
```

---

#### 5.2.3 AddRequest.vue（要望登録）

**責務**:
- 新規要望登録フォーム表示
- バリデーション
- API送信

**主要データ**:
```javascript
data() {
  return {
    form: {
      content: '',
      requesterDepartment: '',
      requesterName: ''
    },
    rules: {
      content: [
        v => !!v || '要望内容は必須です'
      ]
    }
  }
}
```

**主要メソッド**:
```javascript
methods: {
  async submitRequest()   // フォーム送信
  resetForm()             // フォームリセット
}
```

---

### 5.3 ルーティング設計

**ファイル**: [frontend/src/router/index.js](../../../frontend/src/router/index.js)

```javascript
const routes = [
  {
    path: '/',
    name: 'RequestList',
    component: () => import('../components/RequestList.vue')
  },
  {
    path: '/add-request',
    name: 'AddRequest',
    component: () => import('../components/AddRequest.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_URL),
  routes
})
```

**ベースURL**:
- 開発: `/`
- 本番: `/requestForm/`

---

### 5.4 状態管理

**現状**: 各コンポーネント内でローカル状態管理（Vue 3 Composition API未使用）

**将来的な改善案**:
- Pinia導入によるグローバル状態管理
- ユーザー認証状態の管理
- 要望データのキャッシュ管理

---

### 5.5 スタイリング

**Material Design 3**:
- Vuetifyによる統一されたデザインシステム
- カスタムテーマ未設定（デフォルトテーマ使用）

**レスポンシブブレークポイント**:
```
xs: 0px〜599px       (Extra Small - Mobile)
sm: 600px〜959px     (Small - Mobile Landscape)
md: 960px〜1279px    (Medium - Tablet)
lg: 1280px〜1919px   (Large - Desktop)
xl: 1920px〜         (Extra Large - Large Desktop)
```

**色設計**:
- プライマリーカラー: Vuetifyデフォルト（青系）
- ステータスバッジ: 各ステータスに応じた色
- 対応企業チップ: `getHandlerColor()`で定義

---

## 6. バックエンド設計

### 6.1 ディレクトリ構造

```
cgi-bin/requestForm_api/
├── app.py                        # Flaskアプリケーション本体
├── db_migration.py               # データベースマイグレーションツール
├── backup_db.sh                  # データベースバックアップスクリプト
├── .env                          # 環境変数（開発用）
├── .env_for_mySQL                # 環境変数（本番用）
├── requirements.txt              # Python依存パッケージ
├── venv/                         # Python仮想環境
├── migrations/                   # マイグレーションファイル
│   └── migration_add_handler_company.json
├── backups/                      # データベースバックアップ
│   ├── backup_YYYYMMDD_HHMMSS.sql.gz
│   └── backup_log.txt
└── request_management.db         # 開発用SQLiteデータベース
```

### 6.2 Flaskアプリケーション構造

**ファイル**: [cgi-bin/requestForm_api/app.py](../../../cgi-bin/requestForm_api/app.py)

#### 6.2.1 アプリケーション初期化

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import uuid
import os

app = Flask(__name__)

# 環境変数からDB接続情報を読み込み
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///../request_management.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# タイムゾーン設定
jst = timezone(timedelta(hours=9))
```

#### 6.2.2 モデル定義

**Requestモデル**:
```python
class Request(db.Model):
    __tablename__ = 'Requests'

    request_uuid = db.Column(db.String(36), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    requester_department = db.Column(db.String(255))
    requester_name = db.Column(db.String(255))
    input_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='未対応')
    response_comment = db.Column(db.Text)
    assigned_department = db.Column(db.String(255))
    assigned_person = db.Column(db.String(255))
    update_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'request_uuid': self.request_uuid,
            'content': self.content,
            'requester_department': self.requester_department,
            'requester_name': self.requester_name,
            'input_date': self.input_date.replace(tzinfo=timezone.utc).astimezone(jst).isoformat() if self.input_date else None,
            'status': self.status,
            'response_comment': self.response_comment,
            'assigned_department': self.assigned_department,
            'assigned_person': self.assigned_person,
            'update_date': self.update_date.replace(tzinfo=timezone.utc).astimezone(jst).isoformat() if self.update_date else None
        }
```

**Responseモデル**:
```python
class Response(db.Model):
    __tablename__ = 'Responses'

    response_uuid = db.Column(db.String(36), primary_key=True)
    request_uuid = db.Column(db.String(36), db.ForeignKey('Requests.request_uuid', ondelete='CASCADE'), nullable=False)
    handler_company = db.Column(db.String(255))
    handler_department = db.Column(db.String(255))
    handler_name = db.Column(db.String(255))
    status = db.Column(db.String(50), default='未対応')
    response_comment = db.Column(db.Text)
    final_response = db.Column(db.Text)
    response_date = db.Column(db.DateTime, default=datetime.utcnow)
    final_response_date = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'response_uuid': self.response_uuid,
            'request_uuid': self.request_uuid,
            'handler_company': self.handler_company,
            'handler_department': self.handler_department,
            'handler_name': self.handler_name,
            'status': self.status,
            'response_comment': self.response_comment,
            'final_response': self.final_response,
            'response_date': self.response_date.replace(tzinfo=timezone.utc).astimezone(jst).isoformat() if self.response_date else None,
            'final_response_date': self.final_response_date.replace(tzinfo=timezone.utc).astimezone(jst).isoformat() if self.final_response_date else None
        }
```

#### 6.2.3 エンドポイント実装例

```python
@app.route('/requests', methods=['GET'])
def get_requests():
    """全要望を取得"""
    requests = Request.query.all()
    return jsonify([req.to_dict() for req in requests])

@app.route('/requests', methods=['POST'])
def create_request():
    """新規要望を作成"""
    data = request.json

    if not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400

    new_request = Request(
        request_uuid=str(uuid.uuid4()),
        content=data['content'],
        requester_department=data.get('requester_department'),
        requester_name=data.get('requester_name')
    )

    db.session.add(new_request)
    db.session.commit()

    return jsonify({
        'message': 'Request created successfully',
        'request_uuid': new_request.request_uuid
    }), 201
```

---

### 6.3 データベース移行ツール

**ファイル**: [cgi-bin/requestForm_api/db_migration.py](../../../cgi-bin/requestForm_api/db_migration.py)

#### 機能:
1. データベースバックアップ
2. スキーマエクスポート
3. マイグレーションファイル作成
4. マイグレーション適用

#### 使用例:

```bash
# バックアップ作成
python db_migration.py --backup

# スキーマエクスポート
python db_migration.py --export-schema

# マイグレーション適用
python db_migration.py --apply migrations/migration_xxx.json
```

---

### 6.4 バックアップシステム

**ファイル**: [cgi-bin/requestForm_api/backup_db.sh](../../../cgi-bin/requestForm_api/backup_db.sh)

#### 機能:
- MySQLデータベースの日次バックアップ
- gzip圧縮
- 30日以上古いバックアップの自動削除
- バックアップログ記録

#### 推奨cron設定:

```bash
# 毎日午前3時にバックアップ実行
0 3 * * * cd /home/username/www/cgi-bin/requestForm_api && bash backup_db.sh
```

---

## 7. デプロイメント構成

### 7.1 環境構成

#### 7.1.1 開発環境

**フロントエンド**:
```bash
cd frontend
npm install
npm run dev
```
- URL: `http://localhost:5173`
- API URL: `http://127.0.0.1:5000`

**バックエンド**:
```bash
cd cgi-bin/requestForm_api
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
- URL: `http://127.0.0.1:5000`
- Database: SQLite (`request_management.db`)

---

#### 7.1.2 本番環境

**サーバー**: さくらインターネット レンタルサーバー
**ドメイン**: https://felddorf.sakura.ne.jp

**ディレクトリ構成**:
```
~/www/
├── cgi-bin/
│   ├── index.cgi                    # CGIエントリーポイント
│   └── requestForm_api/
│       ├── app.py
│       ├── .env                     # 本番設定(.env_for_mySQL をコピー)
│       ├── venv/
│       ├── requirements.txt
│       └── backups/
├── requestForm/
│   ├── index.html
│   ├── assets/
│   │   ├── index-xxxxx.js
│   │   └── index-xxxxx.css
│   └── ...
```

**環境変数**:

`.env` (本番):
```bash
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=mysql+pymysql://[データベース名]:[DBパスワード]@[MySQLホスト名]/[データベース名]
API_PREFIX=/requestForm_api
```

---

### 7.2 デプロイ手順

#### 7.2.1 フロントエンドデプロイ

```bash
# 1. ビルド
cd frontend
npm install
npm run build

# 2. dist/の内容を確認
ls -la dist/

# 3. サーバーへアップロード
# FTPクライアントまたはscp/rsyncで ~/www/requestForm/ へアップロード
scp -r dist/* username@felddorf.sakura.ne.jp:~/www/requestForm/
```

---

#### 7.2.2 バックエンドデプロイ

```bash
# 1. SSH接続
ssh username@felddorf.sakura.ne.jp

# 2. ディレクトリ移動
cd ~/www/cgi-bin/requestForm_api

# 3. 仮想環境セットアップ（初回のみ）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. 環境変数設定
cp .env_for_mySQL .env
# .envを編集して本番設定を確認

# 5. index.cgiのパーミッション設定
cd ../
chmod 755 index.cgi

# 6. 動作確認
curl https://felddorf.sakura.ne.jp/requestForm_api/requests
```

**index.cgi**:
```python
#!/usr/bin/env python3
import sys
import os

# 仮想環境のパスを追加
sys.path.insert(0, '/home/username/www/cgi-bin/requestForm_api/venv/lib/python3.x/site-packages')
sys.path.insert(0, '/home/username/www/cgi-bin/requestForm_api')

# Flaskアプリをインポート
from app import app

# WSGI互換のCGIハンドラ
from wsgiref.handlers import CGIHandler
CGIHandler().run(app)
```

---

### 7.3 デプロイチェックリスト

#### フロントエンド

- [ ] `.env.production`に正しいAPI URLとベースURLを設定
- [ ] `npm run build`でエラーがないこと
- [ ] `dist/`フォルダが正しく生成されていること
- [ ] `~/www/requestForm/`にすべてのファイルがアップロードされていること
- [ ] ブラウザで`https://felddorf.sakura.ne.jp/requestForm/`にアクセスできること

#### バックエンド

- [ ] `.env`ファイルが本番設定になっていること
- [ ] `requirements.txt`のパッケージがすべてインストールされていること
- [ ] `index.cgi`が実行可能（chmod 755）であること
- [ ] MySQLデータベースに接続できること
- [ ] テーブルが正しく作成されていること
- [ ] API エンドポイントが正常に応答すること

#### データベース

- [ ] MySQLサーバーに接続できること
- [ ] データベース`[データベース名]`が存在すること
- [ ] テーブル`Requests`, `Responses`が存在すること
- [ ] バックアップスクリプトが動作すること
- [ ] cronジョブが設定されていること（任意）

---

## 8. セキュリティ設計

### 8.1 現状のセキュリティ実装

#### 8.1.1 通信の暗号化

- **HTTPS**: 本番環境ではHTTPS通信を使用
- **証明書**: さくらインターネット提供のSSL証明書

#### 8.1.2 認証

**クライアント側パスワード認証**:
```javascript
// RequestList.vue
const UPDATE_PASSWORD = '[操作パスワード]'
const DELETE_PASSWORD = '[操作パスワード]'

if (password !== UPDATE_PASSWORD) {
  alert('パスワードが正しくありません')
  return
}
```

**問題点**:
- パスワードがソースコードにハードコーディング
- サーバー側での検証がない
- ユーザー管理機能がない

#### 8.1.3 認可

**管理者モード**:
```javascript
// App.vue
data() {
  return {
    isAdminMode: false  // クライアント側のフラグ
  }
}
```

**問題点**:
- クライアント側のみでモード切替
- サーバー側での権限チェックがない
- ブラウザコンソールから容易に変更可能

---

### 8.2 セキュリティリスクと対策

#### 8.2.1 認証・認可の脆弱性

**リスク**: パスワードがハードコーディングされており、誰でもソースを見れば取得可能

**推奨対策**:
1. **JWT認証の導入**:
```python
# Flask-JWT-Extended を使用
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    # ユーザー認証ロジック
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/requests', methods=['DELETE'])
@jwt_required()
def delete_request():
    # 認証済みユーザーのみアクセス可能
    ...
```

2. **ユーザー管理テーブルの追加**:
```sql
CREATE TABLE Users (
    user_uuid VARCHAR(36) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',  -- 'admin', 'user'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

3. **役割ベースのアクセス制御（RBAC）**:
```python
from functools import wraps
from flask_jwt_extended import get_jwt_identity

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@app.route('/requests/<uuid>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_request(uuid):
    ...
```

---

#### 8.2.2 SQLインジェクション

**現状**: SQLAlchemyのORMを使用しているため、基本的に安全

**推奨対策**:
- 生SQLクエリを使用する場合は必ずパラメータバインディングを使用
- ユーザー入力を直接SQLに埋め込まない

**悪い例**:
```python
# 絶対にやってはいけない
query = f"SELECT * FROM Requests WHERE content LIKE '%{user_input}%'"
```

**良い例**:
```python
# パラメータバインディング使用
Request.query.filter(Request.content.like(f'%{user_input}%')).all()
```

---

#### 8.2.3 XSS (Cross-Site Scripting)

**現状**: Vueの自動エスケープにより一定の保護

**推奨対策**:
1. **v-htmlの使用を避ける**
2. **サーバー側でもHTMLエスケープ**:
```python
from markupsafe import escape

@app.route('/requests', methods=['POST'])
def create_request():
    data = request.json
    content = escape(data['content'])  # HTMLエスケープ
    ...
```

3. **Content Security Policy (CSP)の設定**:
```python
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

---

#### 8.2.4 CSRF (Cross-Site Request Forgery)

**現状**: CSRF保護なし

**推奨対策**:
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('CSRF_SECRET_KEY')
```

---

#### 8.2.5 機密情報の管理

**リスク**: データベース認証情報がソースコードに含まれている

**推奨対策**:
1. **環境変数の使用**: 既に実装済み（`.env`ファイル）
2. **`.env`ファイルをGit管理から除外**:
```bash
# .gitignore
.env
.env_for_mySQL
*.db
```

3. **秘密情報管理サービスの利用** (将来的):
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

---

### 8.3 セキュリティベストプラクティス

1. **定期的なセキュリティアップデート**:
```bash
# 依存パッケージの更新
npm audit fix
pip list --outdated
```

2. **入力値のバリデーション**:
```python
from flask import request
from marshmallow import Schema, fields, ValidationError

class RequestSchema(Schema):
    content = fields.Str(required=True, validate=lambda x: len(x) > 0)
    requester_department = fields.Str()
    requester_name = fields.Str()

@app.route('/requests', methods=['POST'])
def create_request():
    schema = RequestSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    ...
```

3. **レート制限**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/requests', methods=['POST'])
@limiter.limit("10 per minute")
def create_request():
    ...
```

4. **ログ記録と監査**:
```python
import logging

logging.basicConfig(filename='app.log', level=logging.INFO)

@app.route('/requests/<uuid>', methods=['DELETE'])
def delete_request(uuid):
    logging.info(f'Request deleted: {uuid} by user: {current_user}')
    ...
```

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|---------|--------|
| 1.0 | 2026-01-05 | 初版作成（引き渡し版） | - |

---

**以上**
