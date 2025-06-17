from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from agent.data_agent import data_agent, sql_dict
from agent.echarts_agent import echarts_agent
from schemas.db_conn_config import DatabaseConnectionConfig
from utils.logger import logger
from utils.test_connection import test_connection

global_conn_config = None


# 应用生命周期管理
@asynccontextmanager
async def lifespan(fast_api_app: FastAPI):
    # 启动时执行
    logger.info("Application starting up...")

    yield  # 应用运行期间

    # 关闭时执行
    logger.info("Application shutting down...")

    # 在这里可以清理资源
    logger.info("Resources cleaned up")


# 创建FastAPI应用
app = FastAPI(
    title="MySQL数据库查询智能体",
    description="指定数据库链接地址，通过自然语言与数据库进行查询交互",
    version="0.1.0",
    lifespan=lifespan
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"发生异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部出错"},
    )


# 基础健康检查端点
@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "OK"}


@app.put("/api/connect")
async def set_connect(config: DatabaseConnectionConfig):
    test_result = await test_connection(config)
    if not test_result:
        return {"success": False, "message": "数据库连接测试失败"}
    global global_conn_config
    global_conn_config = config
    return {"success": True, "message": "数据库连接设置成功"}


@app.post("/api/query")
async def query(query_text: str = Body(..., examples=["查询用户数"])):
    if not global_conn_config:
        return {"success": False, "message": "请先设置数据库连接"}

    logger.info(f"用户查询内容: {query_text}")
    data_agent_result = await data_agent.run(query_text, deps=global_conn_config)
    data_details = data_agent_result.output

    logger.info(f"数据智能体结果: {data_details}")

    echarts_agent_result = None
    if data_details.chart:
        echarts_agent_result = await echarts_agent.run(
            f"MarkDown数据描述：{data_details.markdown_describe} \n 生成的图表类型：{data_details.chart_type}"
        )

    data_text = (
        f"{data_details.markdown_describe}"
        f"\n\n\n"
        f"---"
        f"\n\n\n"
        f"执行的SQL：\n\n{sql_dict.get('sql_text', '无')}"
    )

    result = {
        "data": data_text,
        "chart": echarts_agent_result.output if echarts_agent_result else None,
    }

    return {"success": True, "message": result}


# 静态页面
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    # 启动uvicorn服务器
    logger.info("Starting Uvicorn server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,  # 禁用uvicorn的日志配置，使用loguru
        access_log=False  # 禁用uvicorn的访问日志
    )
