from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = Field(
        default='sqlite:///app.db',
        env="SQLALCHEMY_DATABASE_URI",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = Field(
        default=False,
        env="SQLALCHEMY_TRACK_MODIFICATIONS",
    )

    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    SECURITY_PASSWORD_SALT: str = Field(..., env="SECURITY_PASSWORD_SALT")

    MAIL_SERVER: str = Field(..., env="MAIL_SERVER")
    MAIL_PORT: int = Field(default=587, env="MAIL_PORT")
    MAIL_USE_TLS: bool = Field(default=True, env="MAIL_USE_TLS")
    MAIL_USE_SSL: bool = Field(default=False, env="MAIL_USE_SSL")
    MAIL_USERNAME: str = Field(..., env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., env="MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str = Field(..., env="MAIL_DEFAULT_SENDER")

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
