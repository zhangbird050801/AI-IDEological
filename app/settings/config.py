import os
import typing

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VERSION: str = "0.1.0"
    APP_TITLE: str = "AI-IDEological"
    PROJECT_NAME: str = "AI-IDEological"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: typing.List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List = ["*"]
    CORS_ALLOW_HEADERS: typing.List = ["*"]

    DEBUG: bool = True

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")
    SECRET_KEY: str = "3488a63e1765035d386f05409663f55c83bfae3b3c61a932744b20ad14244dcf"  # openssl rand -hex 32
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day
    # Database URL - 可以通过环境变量 DATABASE_URL 覆盖
    DATABASE_URL: str = "mysql://root:root@localhost:3306/AIdata"

    TORTOISE_ORM: dict = {
        "connections": {
            # MySQL/MariaDB configuration (默认)
            "default": {
                "engine": "tortoise.backends.mysql",
                "credentials": {
                    "host": "localhost",  # Database host address
                    "port": 3306,  # Database port
                    "user": "root",  # Database username
                    "password": "root",  # Database password - 修改为你的实际密码
                    "database": "AIdata",  # Database name
                },
            },
        },
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],
                "default_connection": "default",
            },
        },
        "use_tz": False,  # Whether to use timezone-aware datetimes
        "timezone": "Asia/Shanghai",  # Timezone setting
    }
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # AIGC configuration (read from .env)
    DEEPSEEK_API_KEY: str | None = None
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com"
    MOONSHOT_API_KEY: str | None = None
    MOONSHOT_API_BASE: str = "https://api.moonshot.cn/v1"
    AIGC_PROVIDER: str = "deepseek"
    AIGC_MODEL: str = "deepseek-chat"
    AIGC_TIMEOUT: str | int = 60000

    # Ensure pydantic reads the project's .env file (project root)
    # BASE_DIR was defined above as the project root directory
    model_config = {
        "env_file": os.path.join(BASE_DIR, ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()
