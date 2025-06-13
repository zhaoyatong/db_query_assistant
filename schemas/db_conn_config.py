from pydantic import BaseModel, Field, SecretStr


class DatabaseConnectionConfig(BaseModel):
    """数据库连接请求参数"""
    host: str = Field(..., description="数据库主机地址")
    port: int = Field(3306, gt=0, le=65535, description="数据库端口")
    username: str = Field(..., description="数据库账号")
    password: SecretStr = Field(..., description="数据库密码")  # 敏感字段特殊处理
    database_name: str = Field(..., alias="dbName", description="目标数据库名")

    class Config:
        # 额外配置示例
        json_schema_extra = {
            "example": {
                "host": "mysql.prod.example.com",
                "port": 3306,
                "username": "admin",
                "password": "strongpassword123",
                "dbName": "my_database",
            }
        }
