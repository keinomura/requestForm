# セキュリティガイド

## ⚠️ 重要なセキュリティ上の注意事項

このドキュメントは、要望管理システムの現在のセキュリティ状況と、引き渡し後に実施すべきセキュリティ改善について説明します。

---

## 1. 現在のセキュリティ状況

### 🔴 **重大な問題**

#### 1.1 パスワードのハードコーディング

**影響度**: 高

**現状**:
- フロントエンドのソースコード（`frontend/src/components/RequestList.vue`）に操作パスワードがハードコーディングされている
- ビルド後のJavaScriptファイルにも平文で含まれるため、誰でも閲覧可能

**リスク**:
- ブラウザの開発者ツールで簡単にパスワードを確認できる
- GitHubリポジトリが公開されている場合、全世界に公開される
- 不正な要望の削除や更新が可能

**暫定対策**:
- パスワードを定期的に変更する（ただし、根本的な解決にはならない）

**恒久対策**:
- バックエンドでの認証システムの実装（推奨）
- 環境変数を使用した認証情報の管理

---

#### 1.2 クライアント側のみでの権限チェック

**影響度**: 高

**現状**:
- 管理者モードの切り替えがクライアント側のみで実装されている
- APIエンドポイントに認証・認可がない

**リスク**:
- ブラウザコンソールで管理者モードを有効化できる
- APIを直接叩くことで、パスワードなしで削除や更新が可能

**恒久対策**:
- サーバー側での認証・認可の実装
- JWTトークンによる認証
- 役割ベースのアクセス制御（RBAC）

---

### 🟡 **中程度の問題**

#### 1.3 データベース認証情報の管理

**影響度**: 中

**現状**:
- `.env_for_mySQL`ファイルにデータベースパスワードが平文で保存されている
- バックアップスクリプト（修正前）にパスワードがハードコーディングされていた

**対策済み**:
- ✅ バックアップスクリプトを環境変数から読み込むように修正
- ✅ `.env_for_mySQL`を`.gitignore`に追加
- ✅ テンプレートファイル（`.env_for_mySQL.template`）を作成

**残存リスク**:
- サーバー上の`.env`ファイルへのアクセス権限管理が必要
- パスワードが漏洩した場合の影響が大きい

**追加推奨対策**:
- 定期的なパスワード変更
- データベースユーザーの権限を必要最小限に制限
- ファイルのパーミッション設定（600または640）

---

## 2. セキュリティ改善ロードマップ

### フェーズ1: 即座に実施すべき対策（引き渡し前）

- [x] バックアップスクリプトから認証情報を削除
- [x] `.gitignore`に機密ファイルを追加
- [x] テンプレートファイルの作成
- [ ] パスワードの変更
- [ ] `.env`ファイルのパーミッション設定（`chmod 600`）
- [ ] 認証情報の安全な引き継ぎ（パスワードマネージャー使用）

### フェーズ2: 短期（1〜2ヶ月以内）

- [ ] バックエンドでの認証システムの実装
- [ ] JWT認証の導入
- [ ] APIエンドポイントへの認証追加
- [ ] ユーザー管理機能の実装
- [ ] セッション管理の実装

### フェーズ3: 中期（3〜6ヶ月以内）

- [ ] 役割ベースのアクセス制御（RBAC）
- [ ] 監査ログの実装
- [ ] 多要素認証（MFA）の検討
- [ ] セキュリティヘッダーの設定
- [ ] CSRF保護の実装

### フェーズ4: 長期（6ヶ月以降）

- [ ] セキュリティ監査の実施
- [ ] ペネトレーションテストの実施
- [ ] セキュリティ教育の実施
- [ ] インシデント対応計画の策定

---

## 3. 認証システム実装ガイド

### 3.1 推奨アーキテクチャ

```
[クライアント]
    ↓
    ① ログイン（ユーザー名・パスワード）
    ↓
[バックエンド API]
    ↓
    ② 認証情報の検証
    ↓
    ③ JWTトークンの発行
    ↓
[クライアント]
    ↓
    ④ トークンをローカルストレージに保存
    ↓
    ⑤ API リクエスト時にトークンを送信
    ↓
[バックエンド API]
    ↓
    ⑥ トークンの検証
    ↓
    ⑦ 権限チェック
    ↓
    ⑧ レスポンス返却
```

### 3.2 実装例（Flask + JWT）

#### バックエンド実装

**必要なパッケージ**:
```bash
pip install Flask-JWT-Extended bcrypt
```

**ユーザーモデル**:
```python
# models.py
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')  # 'admin', 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
```

**認証エンドポイント**:
```python
# app.py
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(
            identity=user.user_id,
            additional_claims={'role': user.role}
        )
        return jsonify(access_token=access_token), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/requests/<uuid>', methods=['DELETE'])
@jwt_required()
def delete_request(uuid):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    # 管理者のみ削除可能
    if user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    # 削除処理
    request_obj = Request.query.get(uuid)
    if not request_obj:
        return jsonify({'error': 'Request not found'}), 404

    db.session.delete(request_obj)
    db.session.commit()

    return jsonify({'message': 'Request deleted successfully'}), 200
```

#### フロントエンド実装

**認証サービス**:
```javascript
// src/services/auth.js
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

export const authService = {
  async login(username, password) {
    const response = await axios.post(`${API_URL}/auth/login`, {
      username,
      password
    })

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
    }

    return response.data
  },

  logout() {
    localStorage.removeItem('token')
  },

  getToken() {
    return localStorage.getItem('token')
  },

  isAuthenticated() {
    return !!this.getToken()
  }
}
```

**Axiosインターセプター**:
```javascript
// src/plugins/axios.js
import axios from 'axios'
import { authService } from '@/services/auth'

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL
})

// リクエストインターセプター
axiosInstance.interceptors.request.use(
  (config) => {
    const token = authService.getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default axiosInstance
```

---

## 4. パスワードポリシー

### 4.1 推奨パスワード要件

- 最小長: 12文字以上
- 大文字・小文字を含む
- 数字を含む
- 特殊文字を含む
- 辞書に載っている単語を避ける
- ユーザー名やメールアドレスを含まない

### 4.2 パスワード管理

**推奨ツール**:
- 1Password
- Bitwarden
- LastPass
- KeePass

**禁止事項**:
- 平文でのパスワード保存
- メール・Slackでのパスワード送信
- 複数サービスでの同じパスワードの使用

---

## 5. セキュリティチェックリスト

### 開発時

- [ ] 新しいコードに機密情報が含まれていないか確認
- [ ] 環境変数を使用して設定を管理
- [ ] 入力値のバリデーションを実装
- [ ] SQLインジェクション対策（ORMの使用）
- [ ] XSS対策（自動エスケープの確認）
- [ ] CSRF対策

### デプロイ時

- [ ] `.env`ファイルが`.gitignore`に含まれているか
- [ ] 本番環境の認証情報が正しく設定されているか
- [ ] HTTPSが有効になっているか
- [ ] ファイルパーミッションが適切か
- [ ] 不要なデバッグ情報が無効化されているか

### 運用時

- [ ] 定期的なパスワード変更
- [ ] アクセスログの監視
- [ ] セキュリティアップデートの適用
- [ ] バックアップの定期実行と確認
- [ ] 脆弱性スキャンの実施

---

## 6. インシデント対応

### 6.1 セキュリティインシデントの種類

1. **データ漏洩**: パスワードや個人情報の漏洩
2. **不正アクセス**: 権限のないユーザーによるアクセス
3. **データ改ざん**: 不正なデータの変更や削除
4. **サービス妨害**: システムの可用性への攻撃

### 6.2 インシデント発生時の対応手順

1. **検知・報告**
   - インシデントを検知したら即座に報告
   - 影響範囲の初期評価

2. **初動対応**
   - 被害の拡大を防ぐ
   - ログの保全
   - 関係者への通知

3. **調査**
   - 原因の特定
   - 影響範囲の詳細調査
   - ログの分析

4. **復旧**
   - システムの復旧
   - データのリストア（必要な場合）
   - パスワードの変更

5. **事後対応**
   - インシデントレポートの作成
   - 再発防止策の実施
   - 関係者への報告

### 6.3 緊急連絡先

| 役割 | 連絡先 |
|------|--------|
| システム管理者 | [連絡先] |
| SE部責任者 | [連絡先] |
| セキュリティ担当 | [連絡先] |

---

## 7. 参考資料

### セキュリティガイドライン

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [Vue.js Security](https://vuejs.org/guide/best-practices/security.html)

### 認証・認可

- [JWT.io](https://jwt.io/)
- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [OAuth 2.0](https://oauth.net/2/)

---

## 改訂履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|-----------|------|---------|--------|
| 1.0 | 2026-01-05 | 初版作成 | - |

---

**このドキュメントは定期的に見直し、最新のセキュリティ情報を反映してください。**
