from pydantic_ai import Agent, settings, RunContext
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Scatter, Radar, Funnel, Boxplot, HeatMap, WordCloud


async def generate_bar_chart(
        title: str,
        x_data: list,
        y_data: list,
        series_name: str = "系列1",
        width: str = "800px",
        height: str = "500px"
) -> str:
    """
    生成柱状图
    :param title: 图表标题
    :param x_data: x轴数据
    :param y_data: y轴数据
    :param series_name: 系列名称
    :param width: 图表宽度
    :param height: 图表高度
    :return: 生成的html文件路径
    """
    bar = (
        Bar(init_opts=opts.InitOpts(width=width, height=height))
        .add_xaxis(x_data)
        .add_yaxis(series_name, y_data)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            toolbox_opts=opts.ToolboxOpts(),
            datazoom_opts=opts.DataZoomOpts(),
        )
    )
    return bar.render_embed()


async def generate_line_chart(
        title: str,
        x_data: list,
        y_data: list,
        series_name: str = "系列1",
        width: str = "800px",
        height: str = "500px",
        is_smooth: bool = False,
        is_area: bool = False
) -> str:
    """
    生成折线图
    :param title: 图表标题
    :param x_data: x轴数据
    :param y_data: y轴数据
    :param series_name: 系列名称
    :param width: 图表宽度
    :param height: 图表高度
    :param is_smooth: 是否平滑曲线
    :param is_area: 是否显示面积
    :return: 生成的html文件路径
    """
    line = (
        Line(init_opts=opts.InitOpts(width=width, height=height))
        .add_xaxis(x_data)
        .add_yaxis(
            series_name,
            y_data,
            is_smooth=is_smooth,
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5) if is_area else None
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            toolbox_opts=opts.ToolboxOpts(),
            datazoom_opts=opts.DataZoomOpts(),
        )
    )
    return line.render_embed()


async def generate_pie_chart(
        title: str,
        data: list,
        width: str = "800px",
        height: str = "500px",
        rose_type: str = None
) -> str:
    """
    生成饼图
    :param title: 图表标题
    :param data: 数据格式 [(name1, value1), (name2, value2), ...]
    :param width: 图表宽度
    :param height: 图表高度
    :param rose_type: 玫瑰图类型 (None/'radius'/'area')
    :return: 生成的html文件路径
    """
    pie = (
        Pie(init_opts=opts.InitOpts(width=width, height=height))
        .add(
            "",
            data,
            radius=["30%", "75%"] if rose_type else "75%",
            rosetype=rose_type,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
    )
    return pie.render_embed()


async def generate_scatter_chart(
        title: str,
        x_data: list,
        y_data: list,
        width: str = "800px",
        height: str = "500px"
) -> str:
    """
    生成散点图
    :param title: 图表标题
    :param x_data: x轴数据
    :param y_data: y轴数据 (长度应与x_data相同)
    :param width: 图表宽度
    :param height: 图表高度
    :return: 生成的html文件路径
    """

    # 创建图表对象
    scatter = Scatter(init_opts=opts.InitOpts(width=width, height=height))
    scatter.add_xaxis(xaxis_data=x_data)
    scatter.add_yaxis(
        series_name="",
        y_axis=y_data,
        symbol_size=20,
        label_opts=opts.LabelOpts(is_show=False),
    )
    scatter.set_series_opts()
    scatter.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        toolbox_opts=opts.ToolboxOpts(),
        xaxis_opts=opts.AxisOpts(
            type_="value", splitline_opts=opts.SplitLineOpts(is_show=True)
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
        tooltip_opts=opts.TooltipOpts(is_show=False),
        visualmap_opts=opts.VisualMapOpts(max_=max(y_data)),
    )

    return scatter.render_embed()


async def generate_radar_chart(
        title: str,
        indicators: list,
        values: list,
        series_name: str = "系列1",
        width: str = "600px",
        height: str = "500px"
) -> str:
    """
    生成雷达图
    :param title: 图表标题
    :param indicators: 雷达图指标 [{"name": "指标1", "max": 100}, ...]
    :param values: 数据值
    :param series_name: 系列名称
    :param width: 图表宽度
    :param height: 图表高度
    :return: 生成的html文件路径
    """
    radar = (
        Radar(init_opts=opts.InitOpts(width=width, height=height))
        .add_schema(schema=indicators)
        .add(series_name, [values])
        .set_global_opts(title_opts=opts.TitleOpts(title=title))
    )
    return radar.render_embed()


async def generate_funnel_chart(
        title: str,
        data: list,
        width: str = "800px",
        height: str = "500px",
        sort_: str = "descending"
) -> str:
    """
    生成漏斗图
    :param title: 图表标题
    :param data: 数据格式 [(name1, value1), (name2, value2), ...]
    :param width: 图表宽度
    :param height: 图表高度
    :param sort_: 排序方式 ('ascending'/'descending'/None)
    :return: 生成的html文件路径
    """
    funnel = (
        Funnel(init_opts=opts.InitOpts(width=width, height=height))
        .add(
            "",
            data,
            sort_=sort_,
            label_opts=opts.LabelOpts(position="inside"),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title=title))
    )
    return funnel.render_embed()


async def generate_heatmap_chart(
        title: str,
        x_data: list,
        y_data: list,
        value_data: list,
        width: str = "800px",
        height: str = "500px"
) -> str:
    """
    生成热力图
    :param title: 图表标题
    :param x_data: x轴数据
    :param y_data: y轴数据
    :param value_data: 值数据 [[x_index, y_index, value], ...]
    :param width: 图表宽度
    :param height: 图表高度
    :return: 生成的html文件路径
    """
    heatmap = (
        HeatMap(init_opts=opts.InitOpts(width=width, height=height))
        .add_xaxis(x_data)
        .add_yaxis(
            "",
            y_data,
            value_data,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            visualmap_opts=opts.VisualMapOpts(),
        )
    )
    return heatmap.render_embed()


async def generate_wordcloud_chart(
        title: str,
        data: list,
        width: str = "800px",
        height: str = "500px",
        shape: str = "circle"
) -> str:
    """
    生成词云图
    :param title: 图表标题
    :param data: 数据格式 [(word1, size1), (word2, size2), ...]
    :param width: 图表宽度
    :param height: 图表高度
    :param shape: 形状 ('circle'/'cardioid'/'diamond'/'triangle-forward'/'triangle'/'pentagon'/'star')
    :return: 生成的html文件路径
    """
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(width=width, height=height))
        .add("", data, word_size_range=[12, 60], shape=shape)
        .set_global_opts(title_opts=opts.TitleOpts(title=title))
    )
    return wordcloud.render_embed()


async def generate_boxplot_chart(
        title: str,
        x_data: list,
        y_data: list,
        width: str = "800px",
        height: str = "500px"
) -> str:
    """
    生成箱线图
    :param title: 图表标题
    :param x_data: x轴数据
    :param y_data: y轴数据 (二维数组，每个元素代表一个箱线图的数据点集合)
    :param width: 图表宽度
    :param height: 图表高度
    :return: 生成的html文件路径
    """
    # 确保y_data是二维数组
    if not all(isinstance(item, list) for item in y_data):
        y_data = [y_data]  # 如果是一维数组，转换为二维

    boxplot = (
        Boxplot(init_opts=opts.InitOpts(width=width, height=height))
        .add_xaxis(xaxis_data=x_data)
        .add_yaxis(series_name="", y_axis=Boxplot.prepare_data(y_data))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            toolbox_opts=opts.ToolboxOpts(),
        )
    )

    return boxplot.render_embed()


model_settings = settings.ModelSettings(
    temperature=0.0
)

echarts_agent = Agent[None, str](
    'deepseek:deepseek-chat',
    output_type=[
        generate_bar_chart,
        generate_line_chart,
        generate_pie_chart,
        generate_scatter_chart,
        generate_radar_chart,
        generate_funnel_chart,
        generate_heatmap_chart,
        generate_wordcloud_chart,
        generate_boxplot_chart
    ],
    system_prompt=(
        "你是一个精通于pyecharts和常用统计图的专家，你将收到一组数据和该数据的相关MarkDown格式的描述，以及你要生成的图表类型，"
        "若未告知你具体图表类型，你根据这些数据来判断最适合展示的图表类型。"
        "之后你思考的结果和提供的数据结合后调用对应的工具来生成对应的pyecharts的html内容。"
    ),
    model_settings=model_settings
)
