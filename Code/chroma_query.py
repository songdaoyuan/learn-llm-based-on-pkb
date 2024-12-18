from langchain_chroma import Chroma
from zhipuai_embedding import ZhipuAIEmbeddings

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())    # read local .env file

# 向量数据库持久化路径
persist_directory = '../DataBase/chroma'

# 定义 Embeddings
embedding = ZhipuAIEmbeddings()

# 加载数据库
vectordb = Chroma(
    persist_directory=persist_directory,  # 允许我们将persist_directory目录保存到磁盘上
    embedding_function=embedding
)

print(f"向量数据库中存储的量: {vectordb._collection.count()}")

# question="CORS跨域错误"

# # 余弦相似度检索
# sim_docs = vectordb.similarity_search(question,k=3)
# print(f"检索到的内容数：{len(sim_docs)}")
# for i, sim_doc in enumerate(sim_docs):
#     print(f"检索到的第{i}个内容: \n{sim_doc.page_content[:2000]}", end="\n--------------\n")

# # 最大边际相关性检索
# mmr_docs = vectordb.max_marginal_relevance_search(question,k=3)
# print(f"检索到的内容数：{len(mmr_docs)}")
# for i, sim_doc in enumerate(mmr_docs):
#     print(f"MMR 检索到的第{i}个内容: \n{sim_doc.page_content[:200]}", end="\n--------------\n")