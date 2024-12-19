# 引入 Type Hints 的 feature
from __future__ import annotations
from typing import Dict, List, Any, Optional

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

    client: Optional[Any] = None 
    """`zhipuai.ZhipuAI"""

    def __init__(self, **data):
        """初始化方法，用于实例化 ZhipuAI 客户端"""
        super().__init__(**data)  # 调用 Pydantic 的 BaseModel 初始化
        if self.client is None:
            try:
                from zhipuai import ZhipuAI
                self.client = ZhipuAI()  # 实例化 ZhipuAI 客户端
            except ImportError:
                raise ModuleNotFoundError("No module named 'zhipuai'. Please install it first.")

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
