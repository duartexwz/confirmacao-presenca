"""
Módulo de configuração da aplicação.

Carrega variáveis de ambiente do arquivo `.env` localizado na raiz do projeto
e expõe a instância global `settings` para uso em toda a aplicação.

Variáveis esperadas no `.env`:
    - DB_USER: Usuário do banco de dados PostgreSQL.
    - DB_PASSWORD: Senha do banco de dados PostgreSQL.
    - DB_HOST: Host do banco de dados (padrão: localhost).
    - DB_PORT: Porta do banco de dados (padrão: 5432).
    - DB_NAME: Nome do banco de dados.
    - CORS_ORIGINS: Origens permitidas para CORS, separadas por vírgula
      (padrão: http://localhost:5173).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas a partir de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str

    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def DATABASE_URL(self) -> str:
        """Monta a URL de conexão com o PostgreSQL a partir das partes individuais."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()