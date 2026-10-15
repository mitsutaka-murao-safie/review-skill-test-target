import os


class Settings:
    def __init__(self) -> None:
        self.database_path = os.getenv("DATABASE_PATH", "order_service.db")
        self.max_items_per_order = int(os.getenv("MAX_ITEMS_PER_ORDER", "50"))


settings = Settings()
