"""
运行之前确保工作路径为脚本文件所在的路径
"""

import os
from dotenv import load_dotenv, find_dotenv

# ----------------------------     1.读取配置文件, 指定知识库路径     ----------------------------
_ = load_dotenv(find_dotenv(".env"))
# 手动指定知识库路径
# folder_path = r"../DataBase/KnowledgeDB"
# 使用.env文件指定知识库路径
folder_path = os.environ["KNOWLEDGE_DATABASE_PATH"]
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
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

split_docs = text_splitter.split_documents(doc_pages)

print(split_docs)
print(f"切分后的文件数量：{len(split_docs)}")
print(f"切分后的字符数（可以用来大致评估 token 数）：{sum([len(doc.page_content) for doc in split_docs])}")
# ----------------------------------------------------------------------------------------


# ----------------------------     5.构建向量数据库     ----------------------------
from langchain_chroma import Chroma
from zhipuai_embedding import ZhipuAIEmbeddings

embedding = ZhipuAIEmbeddings()

# 定义持久化路径
persist_directory = '../DataBase/chroma'


# 加载现有的向量数据库（如果已经存在）
try:
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    print("成功加载已有的向量数据库")
except Exception as e:
    print("未找到已有的向量数据库，创建新的向量数据库")
    vectordb = Chroma(embedding_function=embedding, persist_directory=persist_directory)
# 分批处理文档
batch_size = 5  # 每批处理的文档数量，受并发限制应该<=5
total_docs = len(split_docs)  # 总文档数

for i in range(0, total_docs, batch_size):
    # 获取当前批次的文档
    batch_docs = split_docs[i:i+batch_size]
    print(f"正在处理第 {i // batch_size + 1} 批文档，共 {len(batch_docs)} 个文档")

    # 将当前批次的文档添加到向量数据库
    vectordb.add_documents(documents=batch_docs)

    # 持久化存储数据库
    vectordb.persist()
    print(f"第 {i // batch_size + 1} 批文档已保存到向量数据库")

print("所有文档已成功存储到向量数据库")