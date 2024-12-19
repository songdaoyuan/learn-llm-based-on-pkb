# 引入 Type Hints 的 feature
from __future__ import annotations
from typing import Dict, List, Any

# 记录日志信息
import logging


from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, model_validator

# 初始化日志记录器
logger = logging.getLogger(__name__)

"""
目标: 实现自定义 Embeddings

需要定义一个自定义类继承自 LangChain 的 Embeddings 基类, 然后定义两个函数:

embed_query 方法, 用于对单个字符串(query)进行 embedding
embed_documents 方法, 用于对字符串列表(documents)进行 embedding。

源码解析参考 ../Doc/0xC0FFee 代码笔记.md
"""


class ZhipuAIEmbeddings(BaseModel, Embeddings):
    """`Zhipuai Embeddings` embedding models."""

    client: Any
    """`zhipuai.ZhipuAI"""

    @model_validator(mode="after")
    # 声明式、符合 Pydantic 的初始化和校验过程, 类似于__init__
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

    def embed_query(self, text: str) -> List[float]:
        """
        生成输入文本的 embedding.

        Args:
            texts (str): 要生成 embedding 的文本.

        Return:
            embeddings (List[float]): 输入文本的 embedding，一个浮点数值列表.
        """
        embeddings = self.client.embeddings.create(model="embedding-2", input=text)
        return embeddings.data[0].embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        生成输入文本列表的 embedding.
        Args:
            texts (List[str]): 要生成 embedding 的文本列表.

        Returns:
            List[List[float]]: 输入列表中每个文档的 embedding 列表。每个 embedding 都表示为一个浮点值列表。
        """
        return [self.embed_query(text) for text in texts]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronous Embed search docs."""
        raise NotImplementedError(
            "Please use `embed_documents`. Official does not support asynchronous requests"
        )

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronous Embed query text."""
        raise NotImplementedError(
            "Please use `aembed_query`. Official does not support asynchronous requests"
        )
