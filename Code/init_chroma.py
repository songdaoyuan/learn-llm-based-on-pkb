"""
运行之前确保工作路径为脚本文件所在的路径
"""

import os
from dotenv import load_dotenv, find_dotenv

# ----------------------------     1.读取配置文件, 指定知识库路径     ----------------------------
_ = load_dotenv(find_dotenv(".env"))
# 手动指定知识库路径
folder_path = r"../DataBase/KnowledgeDB"
# 使用.env文件指定知识库路径
# folder_path = os.environ["KNOWLEDGE_DATABASE_PATH"]
# -----------------------------------------------------------------------------------------------


# ----------------------------     2.读取知识库中的文件     ----------------------------
file_paths = []
for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        file_paths.append(file_path)
print(file_paths)

# 更新到langchain最新的*Loader引用
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader

# 遍历文件路径并把实例化的loader存放在loaders里
loaders = []

for file_path in file_paths:

    file_type = file_path.split(".")[-1]
    if file_type == "pdf":
        loaders.append(PyMuPDFLoader(file_path))
    elif file_type == "md":
        loaders.append(UnstructuredMarkdownLoader(file_path))

# 加载所有的文件, 存放在doc_pages中
doc_pages = []

for loader in loaders:
    doc_pages.extend(loader.load())
# -------------------------------------------------------------------------------------


# ----------------------------     3.对文档的数据进行清洗     ----------------------------
# 使用正则表达式去除段落内部的换行符, 但保留段落之间的换行 & 去除多余的空格
import re
for doc_page in doc_pages:
    doc_page.page_content = re.sub(r'(?<=\n)\n+(?!\n)', ' ', doc_page.page_content)
    doc_pagepage_content  = doc_page.page_content.replace(' ', '')

    # print(
    #     f"每一个元素的类型：{type(doc_page)}.",
    #     f"该文档的描述性数据：{doc_page.metadata}",
    #     f"查看该文档的内容:\n{doc_page.page_content[0:]}",
    #     sep="\n------\n",
    # )
# ---------------------------------------------------------------------------------------

# ----------------------------     4.对文档的数据进行切分     ----------------------------
# 可以自定义切分方式
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 切分文档
text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)

split_docs = text_splitter.split_documents(doc_pages)

# print(split_docs)
print(f"切分后的文件数量：{len(split_docs)}")
print(f"切分后的字符数（可以用来大致评估 token 数）：{sum([len(doc.page_content) for doc in split_docs])}")
# ----------------------------------------------------------------------------------------


# ----------------------------     5.构建向量数据库     ----------------------------
from zhipuai_embedding import ZhipuAIEmbeddings

embedding = ZhipuAIEmbeddings()

# 定义持久化路径
persist_directory = '../DataBase/chroma'

from langchain.vectorstores.chroma import Chroma

vectordb = Chroma.from_documents(
    documents=split_docs[:5], # 免费版本的API向量模型 Embedding-2 速率限制为5
    embedding=embedding,
    persist_directory=persist_directory  # 允许我们将persist_directory目录保存到磁盘上
)

vectordb.persist()

print(f"向量库中存储的数量：{vectordb._collection.count()}")