# 引入 Type Hints 的 feature
from __future__ import annotations
from typing import Dict, List, Any

# 记录日志信息
import logging


from langchain.embeddings.base import Embeddings
from langchain.pydantic_v1 import BaseModel, root_validator

# 初始化日志记录器
logger = logging.getLogger(__name__)

"""
目标: 实现自定义 Embeddings

需要定义一个自定义类继承自 LangChain 的 Embeddings 基类, 然后定义两个函数:

embed_query 方法, 用于对单个字符串(query)进行 embedding
embed_documents 方法, 用于对字符串列表(documents)进行 embedding。
"""


class ZhipuAIEmbeddings(BaseModel, Embeddings):
    """`Zhipuai Embeddings` embedding models."""

    client: Any
    """`zhipuai.ZhipuAI"""

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """
        实例化ZhipuAI为values["client"]

        Args:

            values (Dict): 包含配置信息的字典, 必须包含 client 的字段.
        Returns:

            values (Dict): 包含配置信息的字典。如果环境中有zhipuai库, 则将返回实例化的ZhipuAI类
                           否则将报错 'ModuleNotFoundError: No module named 'zhipuai''.
        """
        from zhipuai import ZhipuAI

        values["client"] = ZhipuAI()
        return values
