# order-service

小規模 EC 向けの注文管理 API。FastAPI + SQLite。

## 起動

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## テスト

```
pytest
```

## 認証

`Authorization: Bearer <api_token>` ヘッダで認証する。トークンは `users.api_token` に保存されている。
