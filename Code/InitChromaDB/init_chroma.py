"""
运行之前确保工作路径为脚本文件所在的路径
"""

import os

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv("../.env"))

# 文档库路径
folder_path = r"../../DataBase/KnowledgeDB"
# 文档列表
file_paths = []

for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        file_paths.append(file_path)
print(file_paths[:3])

from langchain.document_loaders.pdf import PyMuPDFLoader
from langchain.document_loaders.markdown import UnstructuredMarkdownLoader

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

for loader in loaders: texts.extend(loader.load())

text = texts[1]
print(f"每一个元素的类型：{type(text)}.", 
    f"该文档的描述性数据：{text.metadata}", 
    f"查看该文档的内容:\n{text.page_content[0:]}", 
    sep="\n------\n")