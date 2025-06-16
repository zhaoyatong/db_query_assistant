from pydantic import BaseModel


class DataDetails(BaseModel):
    markdown_describe: str # markdown格式的数据描述
    chart:bool # 是否生成图表
    chart_type: str # 图表类型
