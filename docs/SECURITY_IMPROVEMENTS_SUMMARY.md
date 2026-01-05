# セキュリティ改善実施サマリー

## 実施日: 2026-01-05

---

## 📋 実施した改善

### 1. バックアップスクリプトのセキュリティ強化

**ファイル**: `cgi-bin/requestForm_api/backup_db.sh`

**変更内容**:
- ✅ ハードコーディングされたデータベース認証情報を削除
- ✅ 環境変数（`.env`ファイル）から認証情報を読み込むように変更
- ✅ `DATABASE_URL`をパースして接続情報を抽出する仕組みを実装

**Before**:
```bash
DB_USER="felddorf_request_db"
DB_HOST="mysql3102.db.sakura.ne.jp"
DB_NAME="felddorf_request_db"
DB_PASSWORD="sakura2rental4db"  # ハードコーディング
```

**After**:
```bash
# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Parse DATABASE_URL to extract credentials
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^\/]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
```

---

### 2. 環境変数テンプレートの作成

**ファイル**: `cgi-bin/requestForm_api/.env_for_mySQL.template`

**目的**:
- 実際の認証情報を含まないテンプレートファイルをGit管理
- 新しい環境での設定を容易にする
- セキュリティリスクを低減

**内容**:
```bash
FLASK_ENV=production
FLASK_DEBUG=0
DATABASE_URL=mysql+pymysql://[DBユーザー名]:[DBパスワード]@[MySQLホスト名]/[データベース名]
API_PREFIX=/requestForm_api
```

---

### 3. .gitignore の強化

**ファイル**: `.gitignore`

**追加した除外ルール**:
```gitignore
# Security: Exclude files with actual credentials
.env_for_mySQL
backup_db.sh.production
*.db
*.sqlite
*.sql
*.sql.gz
backups/

# Credentials template file
docs/CREDENTIALS.md
```

**効果**:
- 実際の認証情報を含むファイルがGitにコミットされない
- バックアップファイルやデータベースファイルの誤コミットを防止
- 機密情報の漏洩リスクを低減

---

### 4. ドキュメントからの機密情報削除

**対象ファイル**:
- `README.md`
- `docs/specs/system/01_system_overview.md`
- `docs/specs/technical/01_technical_architecture.md`
- `docs/specs/operations/01_operations_manual.md`
- `docs/HANDOVER_CHECKLIST.md`

**置き換えた情報**:
| 元の値 | 置き換え後 |
|--------|----------|
| `sakura2rental4db` | `[DBパスワード]` |
| `felddorf_request_db` | `[データベース名]` |
| `mysql3102.db.sakura.ne.jp` | `[MySQLホスト名]` |
| `del3377` | `[操作パスワード]` |
| `felddorf.sakura.ne.jp` | `[サーバーホスト名]` |

---

### 5. 新規ドキュメントの作成

#### 5.1 認証情報テンプレート

**ファイル**: `docs/CREDENTIALS_TEMPLATE.md`

**内容**:
- サーバー接続情報のテンプレート
- データベース接続情報のテンプレート
- アプリケーション操作パスワードのテンプレート
- セキュリティベストプラクティス
- 引き渡し時の注意事項

**用途**:
- SE部への引き渡し時に、このテンプレートに実際の値を記入
- パスワードマネージャーや暗号化されたストレージで管理

---

#### 5.2 セキュリティガイド

**ファイル**: `docs/SECURITY.md`

**内容**:
- 現在のセキュリティ状況の詳細説明
- セキュリティ改善ロードマップ
- 認証システム実装ガイド（コード例付き）
- パスワードポリシー
- セキュリティチェックリスト
- インシデント対応手順

**用途**:
- SE部がセキュリティ改善を実施する際のガイド
- 具体的な実装例を提供
- セキュリティベストプラクティスの参照

---

## 🔴 残存する重大なセキュリティ問題

### 1. フロントエンドのパスワードハードコーディング

**ファイル**: `frontend/src/components/RequestList.vue`

**現状**:
```javascript
const UPDATE_PASSWORD = 'del3377'  // ハードコーディング
const DELETE_PASSWORD = 'del3377'  // ハードコーディング
```

**リスク**:
- ブラウザの開発者ツールで誰でも確認可能
- ビルド後のJavaScriptファイルにも平文で含まれる
- GitHubで公開されている場合、全世界に公開される

**なぜ修正しなかったか**:
- フロントエンドだけの修正では根本的な解決にならない
- バックエンドでの認証システムの実装が必要
- 一時的な対処療法は混乱を招く可能性がある

**推奨対策**:
SE部への引き渡し後、早急に以下を実施:
1. バックエンドでの認証API実装
2. JWT認証の導入
3. フロントエンドからのパスワード削除
4. 認証トークンベースの認証に移行

---

### 2. サーバー側の認証・認可の欠如

**現状**:
- すべてのAPIエンドポイントが認証なしでアクセス可能
- クライアント側のパスワードチェックのみ
- 管理者モードの切り替えがクライアント側のみ

**リスク**:
- APIを直接叩くことで、パスワードなしで操作可能
- 不正なデータの削除や改ざんが可能

**推奨対策**:
[docs/SECURITY.md](SECURITY.md) の「3. 認証システム実装ガイド」を参照

---

## ✅ 引き渡し前のチェックリスト

### SE部で実施すべきこと

- [ ] **認証情報の準備**
  - [ ] 新しいデータベースの作成（個人用DBからの移行）
  - [ ] 新しいデータベースパスワードの設定
  - [ ] すべてのパスワードの変更

- [ ] **ファイルの設定**
  - [ ] `CREDENTIALS_TEMPLATE.md`に実際の値を記入
  - [ ] `.env_for_mySQL`を実際の値で作成
  - [ ] サーバー上の`.env`ファイルのパーミッション設定（`chmod 600`）

- [ ] **セキュリティ改善計画の策定**
  - [ ] [docs/SECURITY.md](SECURITY.md) の改善ロードマップを確認
  - [ ] 優先度と実施スケジュールの決定
  - [ ] 担当者のアサイン

- [ ] **Git管理の確認**
  - [ ] `.gitignore`が正しく設定されているか確認
  - [ ] 機密情報を含むファイルがコミット履歴に残っていないか確認
  - [ ] 必要に応じてGit履歴のクリーンアップ

---

## 📚 関連ドキュメント

- [セキュリティガイド](SECURITY.md) - 詳細な対策方法と実装例
- [認証情報テンプレート](CREDENTIALS_TEMPLATE.md) - 機密情報の管理テンプレート
- [技術仕様書 - セキュリティ設計](specs/technical/01_technical_architecture.md#8-セキュリティ設計)
- [運用マニュアル](specs/operations/01_operations_manual.md)
- [引き渡しチェックリスト](HANDOVER_CHECKLIST.md)

---

## 🎯 次のステップ

1. **即座に実施**:
   - パスワードの変更
   - `.env`ファイルのパーミッション設定
   - 認証情報の安全な引き継ぎ

2. **短期（1〜2ヶ月以内）**:
   - バックエンドでの認証システムの実装開始
   - JWT認証の導入
   - フロントエンドからのパスワード削除

3. **中期（3〜6ヶ月以内）**:
   - RBAC（役割ベースのアクセス制御）の実装
   - 監査ログの実装
   - セキュリティテストの実施

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|---------|--------|
| 1.0 | 2026-01-05 | 初版作成 | - |

---

**重要**: このドキュメントは、SE部への引き渡し時に必ず確認してください。
