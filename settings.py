from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from datetime import datetime, date


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    
    start_date: date = Field(alias="start_date")
    end_date: date = Field(alias="end_date")
    
    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def str_to_date(cls, v) -> date:
        return datetime.strptime(v, "%Y-%m-%d").date()
    
    # Due to the task, the system provides file downloading to Yandex Disk 
    yd_token: str = Field(alias="yd_token")
    
    # A bunch of constants you should manually get after the authentication
    auth_token: str = Field(alias="auth_token") 
    auth_bearer: str = Field(alias="auth_bearer")
    textalk: str = Field(alias="textalk")


settings = Settings()
        