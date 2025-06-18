import re
from typing import Any

import aiomysql
from pydantic_ai import Agent, settings, RunContext, ModelRetry

from schemas.agent_output import DataDetails
from schemas.db_conn_config import DatabaseConnectionConfig
from utils.logger import logger

model_settings = settings.ModelSettings(
    temperature=0.0
)

data_agent = Agent(
    'deepseek:deepseek-chat',
    deps_type=DatabaseConnectionConfig,
    output_type=DataDetails,
    system_prompt=(
        "你是一个数据库查询专家，你精通根据用户的问题来结合数据库表和字段信息生成对应的SQL，然后调用对应工具执行SQL，"
        "最后你将SQL查询的结果结合用户的问题以简单易懂的语言输出，并根据用户的问题判断要不要生成统计图表。"
        "数据库中所有表的描述信息可以通过工具来获取，如果获取到的结果是空或空字典等，直接输出“无法读取数据库信息。”。"
        "SQL执行结果可以通过工具来获取，如果查询结果为空，直接输出“未能查询到相关结果。”"
        "若用户直接提供了SQL，直接调用SQL查询工具来执行提供的SQL。"
        "要注意你输出的信息尽量便于阅读，例如永远用名称代替id输出，另外多行数据需要输出时你要用表格形式输出。"
        "为了输出的美观性和易读性，你总是以MarkDown格式输出答案，以Bool类型来输出是否需要生成统计图表，并尽量说明图表类型。"
        "注意：除非用户的问题中明确表示需要生成统计图表，否则一律认为不需要生成统计图表（False），图表名称用中文输出。"
        "注意：不要在答案中包含和问题及答案无关的内容，尤其是自己的思考和执行过程。类似【我将生成图表】这类描述绝对不可以出现在答案中。"
        "注意：一旦你遇到无法确定或无法解决的问题，或者遇到用户随意问了和数据查询不相干的问题，不要自我猜测，直接输出“抱歉，我不能帮你解决这个问题。”。"
    ),
    model_settings=model_settings
)


sql_dict = {}

@data_agent.tool
async def get_db_tables_description(ctx: RunContext[DatabaseConnectionConfig]) -> dict[str, str | dict[str, str]]:
    """
    获取数据库中所有表和列信息（表名、列名、数据类型、列描述和表描述）
    :return:
        dict: {
            表名: {
                "description": 表描述(仅MySQL),
                "columns": [{"name": 列名, "type": 类型, "comment": 列描述}, ...]
            }
        }
    """
    schema = {}

    try:
        async with aiomysql.connect(
                host=ctx.deps.host,
                port=ctx.deps.port,
                user=ctx.deps.username,
                password=ctx.deps.password.get_secret_value(),
                db=ctx.deps.database_name,
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor
        ) as conn:
            async with conn.cursor() as cursor:
                # 获取所有表名和表注释
                await cursor.execute("""
                                     SELECT TABLE_NAME, TABLE_COMMENT
                                     FROM INFORMATION_SCHEMA.TABLES
                                     WHERE TABLE_SCHEMA = DATABASE()
                                     """)
                tables = await cursor.fetchall()

                for table in tables:
                    table_name = table['TABLE_NAME']

                    # 获取列详细信息
                    await cursor.execute(f"""
                                    SELECT 
                                        COLUMN_NAME,
                                        COLUMN_TYPE,
                                        COLUMN_COMMENT
                                    FROM INFORMATION_SCHEMA.COLUMNS 
                                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                                    ORDER BY ORDINAL_POSITION
                                """, (table_name,))

                    columns = await cursor.fetchall()

                    schema[table_name] = {
                        "description": table['TABLE_COMMENT'] or None,
                        "columns": [
                            {
                                "name": col['COLUMN_NAME'],
                                "type": col['COLUMN_TYPE'],
                                "comment": col['COLUMN_COMMENT'] or None,
                            }
                            for col in columns
                        ]
                    }
    except Exception as e:
        logger.error(e)

    return schema


@data_agent.tool(retries=2)
async def execute_sql(ctx: RunContext[DatabaseConnectionConfig], sql: str) -> list[dict[str, Any]] | None:
    """
    执行SQL查询并返回结果
    :param ctx: agent上下文
    :param sql: SQL查询语句
    :return:
        list: 查询结果列表
    """
    logger.info(f"执行SQL查询：{sql}")
    sql_dict.clear()
    sql_dict["sql_text"] = sql

    result = None

    #  检查SQL中是否包含危险操作，但是字段中可能包含update，如update_time
    danger_sql = [
        'update', 'delete', 'insert', 'drop', 'truncate', 'create', 'alter', 'rename', 'grant', 'revoke', 'set', 'optimize',
        'call', 'begin', 'commit', 'rollback', 'lock', 'unlock', 'savepoint', 'execute', 'deallocate', 'kill', 'reset',
    ]
    # 构造正则：匹配单词边界或特定前缀（避免误判字段名）
    pattern = re.compile(
        r'\b(' + '|'.join(danger_sql) + r')\b',
        flags=re.IGNORECASE  # 忽略大小写
    )

    if bool(pattern.search(sql)):
        return None

    try:
        async with aiomysql.connect(
                host=ctx.deps.host,
                port=ctx.deps.port,
                user=ctx.deps.username,
                password=ctx.deps.password.get_secret_value(),
                db=ctx.deps.database_name,
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor
        ) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql)
                result = await cursor.fetchall()

    except Exception as e:
        logger.error(e)
        raise ModelRetry(f"SQL执行错误，错误信息：{e}。")

    return result
