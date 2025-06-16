import asyncio

import aiomysql

from schemas.db_conn_config import DatabaseConnectionConfig
from utils.logger import logger


async def test_connection(conn_config: DatabaseConnectionConfig) -> bool:
    try:
        # 直接创建单个连接（不使用连接池）
        async with await aiomysql.connect(
                host=conn_config.host,
                port=conn_config.port,
                user=conn_config.username,
                password=conn_config.password.get_secret_value(),
                db=conn_config.database_name,
                connect_timeout=5
        ) as conn:
            # 创建游标执行查询
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()

                if result == (1,):
                    return True
                else:
                    return False

    except aiomysql.Error as e:
        logger.error(f"测试数据库链接发生错误: {e}")
        return False
    except asyncio.TimeoutError:
        logger.error("测试数据库链接超时")
        return False
    except Exception as e:
        logger.error(f"测试数据库链接发生错误: {e}")
        return False
