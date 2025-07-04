# MySQL数据库查询小助手

## 介绍
基于大模型的SQL查询小助手，输入任意查询内容，即可返回查询结果。

项目使用了deepseek-v3模型，可自行更换其他模型，若使用其他模型，请自行安装相关依赖。

注意需要在项目启动前配置环境变量：DEEPSEEK_API_KEY（其他模型根据要求配置）。

### 技术栈
1. Web：FastAPI
2. Agent：PydanticAI
3. 环境管理：Poetry
4. 图表生成：pyecharts
5. 数据访问：aiomysql
6. 模型：deepseek-v3