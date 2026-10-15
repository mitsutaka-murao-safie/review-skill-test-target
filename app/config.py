import os


class Settings:
    def __init__(self) -> None:
        self.database_path = os.getenv("DATABASE_PATH", "order_service.db")
        self.max_items_per_order = int(os.getenv("MAX_ITEMS_PER_ORDER", "50"))
        self.invoice_dir = os.getenv("INVOICE_DIR", "/var/lib/order-service/invoices")
        self.payment_api_url = os.getenv("PAYMENT_API_URL", "http://localhost:9")
        self.webhook_url = os.getenv("ORDER_WEBHOOK_URL", "")
        self.webhook_token = os.getenv(
            "ORDER_WEBHOOK_TOKEN", "whk_live_7Qm2c9XvR4pLs8TzK1nB0eYw"
        )


settings = Settings()
