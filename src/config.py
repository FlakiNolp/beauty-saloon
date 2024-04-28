
import os

DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PORT: int = int(os.getenv("DB_PORT", 5432))
DB_HOST: str = os.getenv("DB_HOST", 'localhost')
DB_PASSWORD: str = os.getenv("DB_PASSWORD", 'postgres')
DB_NAME: str = os.getenv("DB_NAME", 'beauty_saloon')
NUMBER_OF_INLINE_BUTTONS: int = int(os.getenv("NUMBER_OF_INLINE_BUTTONS", 2))
