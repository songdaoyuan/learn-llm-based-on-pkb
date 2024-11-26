"""
运行之前确保工作路径为脚本文件所在的路径
"""

import os

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv("../.env"))

# 手动文档库路径
folder_path = r"../../DataBase/KnowledgeDB"
# 使用.env文件指定
# folder_path = os.environ["KNOWLEDGE_DATABASE_PATH"]

# 文档列表
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

# 下载文件并存储到text
texts = []

for loader in loaders:
    texts.extend(loader.load())

# text = texts[1]
# print(
#     f"每一个元素的类型：{type(text)}.",
#     f"该文档的描述性数据：{text.metadata}",
#     f"查看该文档的内容:\n{text.page_content[0:]}",
#     sep="\n------\n",
# )

from langchain.text_splitter import RecursiveCharacterTextSplitter

# 切分文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50)

split_docs = text_splitter.split_documents(texts)
print(split_docs)