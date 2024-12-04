# 0x04 RAG应用的构建

## 将 LLM 接入到 LangChain

### 基于 LangChain 调用 OpenAI / Kimi

1. 模型接入

    LangChain 提供了对于多种大模型的封装, 社区提供了对 Moonshot Chat 的[支持](https://python.langchain.com/docs/integrations/llms/moonshot/#related)，也就是我们熟知的Kimi

    示例代码可以[参考](../Code/LangChainOpenAI.ipynb)

    在初始化LLM对象的时候，可以指定超参数，下面以 OpenAI 的为例

    ```plaintext
    · model_name：所要使用的模型

    · temperature：温度系数，取值同原生接口。

    · openai_api_key：OpenAI API key，如果不使用环境变量设置 API Key，也可以在实例化时设置。

    · openai_proxy：设置代理，如果不使用环境变量设置代理，也可以在实例化时设置。

    · streaming：是否使用流式传输，即逐字输出模型回答，默认为 False，此处不赘述。

    · max_tokens：模型输出的最大 token 数，意义及取值同上。
    ```

    对于其他大模型，可以通过查看官方文档或者 LangChain 源码查看当前大模型API支持哪些超参数

2. 构建 Prompt

    开发大模型应用时，用户输入通常被整合到包含上下文的提示模板中，以提高效率。`PromptTemplates` 负责这一过程，将输入转换为完整格式化的提示。下面是一个个性化的`Template`示例

    ```python
    from langchain_core.prompts import ChatPromptTemplate

    # 这里我们要求模型对给定文本进行中文翻译
    prompt = """请你将由三个反引号分割的文本翻译成英文！\
    text: ```{text}```
    """
    ```

    聊天模型接口处理的是消息而非原始文本。`PromptTemplates` 用于生成消息列表，其中每个消息包含角色和位置信息。`ChatPromptTemplate` 是一系列 `ChatMessageTemplate` 的集合，每个模板负责格式化聊天消息的角色和内容。完整示例如下

    ```python
    from langchain.prompts.chat import ChatPromptTemplate

    template = "你是一个翻译助手，可以帮助我将 {input_language} 翻译成 {output_language}."
    human_template = "{text}"

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_template),
    ])

    text = "我带着比身体重的行李，\
    游入尼罗河底，\
    经过几道闪电 看到一堆光圈，\
    不确定是不是这里。\
    "
    messages  = chat_prompt.format_messages(input_language="中文", output_language="英文", text=text)
    ```

    构建好的`message`内容如下

    ```python
    [SystemMessage(content='你是一个翻译助手，可以帮助我将 中文 翻译成 英文.'),
    HumanMessage(content='我带着比身体重的行李，游入尼罗河底，经过几道闪电 看到一堆光圈，不确定是不是这里。')]
    ```

    通过调用定义好的llm和messages来获取回答

    ```python
    output  = llm.invoke(messages)
    ------
    AIMessage(content='I carried luggage heavier than my body and dived into the bottom of the Nile River. After passing through several flashes of lightning, I saw a pile of halos, not sure if this is the place.')
    ```

    !!!**说明**
        `from langchain_core.prompts import ChatPromptTemplate` 和
        `from langchain.prompts.chat import ChatPromptTemplate` 这两个`ChatPromptTemplate`实际上指向的是同一个类
        LangChain 正在进行架构重组，将核心功能移至 langchain-core 包中，以实现更好的模块化和维护性，推荐使用第一种导入方式，它更稳定且是未来推荐的用法。

    代码示例见[LangChainOpenAI.ipynb #代码块3](../Code/LangChainOpenAI.ipynb)

3. 输出解析器 Output parser

    OutputParsers 将语言模型的原始输出转换为可以在下游使用的格式。 OutputParsers 有几种主要类型，包括：
    * 将 LLM 文本转换为结构化信息（例如 JSON）
    * 将 ChatMessage 转换为字符串
    * 将除消息之外的调用返回的额外信息（如 OpenAI 函数调用）转换为字符串

    最后，我们将模型输出传递给 output_parser，它是一个 BaseOutputParser，这意味着它接受字符串或 BaseMessage 作为输入。 StrOutputParser 特别简单地将任何输入转换为字符串。

    ```python
    from langchain_core.output_parsers import StrOutputParser

    output_parser = StrOutputParser()
    output_parser.invoke(output)
    ```

    输出内容被格式化成了字符串

    ```plaintext
    'I carried luggage heavier than my body and dived into the bottom of the Nile River. After passing through several flashes of lightning, I saw a pile of halos, not sure if this is the place.'
    ```

    代码示例见[LangChainOpenAI.ipynb #代码块4](../Code/LangChainOpenAI.ipynb)

4. 使用 LCEL 构建完整流程链

    !!! **说明**
        LCEL（LangChain Expression Language，Langchain的表达式语言）
        LCEL是一种新的语法，是LangChain工具包的重要补充，他有许多优点，使得我们处理LangChain和代理更加简单方便。

    * LCEL提供了异步、批处理和流处理支持，使代码可以快速在不同服务器中移植。
    * LCEL拥有后备措施，解决LLM格式输出的问题。
    * LCEL增加了LLM的并行性，提高了效率。
    * LCEL内置了日志记录，即使代理变得复杂，有助于理解复杂链条和代理的运行情况。

    示例代码：

    `chain = prompt | model | output_parser`

    LCEL 将不同的组件拼凑成一个链，在此链中，用户输入传递到提示模板，然后提示模板输出传递到模型，然后模型输出传递到输出解析器。| 的符号类似于 Unix 管道运算符，它将不同的组件链接在一起，将一个组件的输出作为下一个组件的输入。

    ```python
    chain = chat_prompt | llm | output_parser
    chain.invoke({"input_language":"中文", "output_language":"英文","text": text})
    ```

    输出内容

    ```plaintext
    'I carried luggage heavier than my body and dived into the bottom of the Nile River. After passing through several flashes of lightning, I saw a pile of halos, not sure if this is the place.'
    ```

    代码示例见[LangChainOpenAI.ipynb #代码块5](../Code/LangChainOpenAI.ipynb)

### 基于 LangChain 调用 智谱 GLM

Todo

## 构建检索问答链

### 加载向量数据库

!!!**说明**
    如果还没有在本地持久化向量数据库
    可以参考[DataProcessing.ipynb](../Code/DataProcessing.ipynb)的内容对原 MD 文档进行处理
    然后参考[ZhipuAIEmbeddingAPI.ipynb](../Code/ZhipuAIEmbeddingAPI.ipynb)和[zhipuai_embedding.py](../Code/zhipuai_embedding.py)
    中的内容, 构建向量数据库并且持久化的存储在本地

加载向量数据库和环境变量

```python
import os
import sys
sys.path.append("../C3 搭建知识库") # 将父目录放入系统路径中

# 使用智谱 Embedding API，注意，需要将上一章实现的封装代码下载到本地
from zhipuai_embedding import ZhipuAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())    # read local .env file
zhipuai_api_key = os.environ['ZHIPUAI_API_KEY']

# 定义 Embeddings
embedding = ZhipuAIEmbeddings()
# 向量数据库持久化路径
persist_directory = '../C3 搭建知识库/data_base/vector_db/chroma'
# 加载数据库
vectordb = Chroma(
    persist_directory=persist_directory,  # 允许我们将persist_directory目录保存到磁盘上
    embedding_function=embedding
)

print(f"向量库中存储的数量：{vectordb._collection.count()}")
```

如果需要测试向量数据库, 可以使用一个问题 query 在向量数据库中根据相似性进行检索，返回前 k 个最相似的文档。

```python
# 使用相似性搜索前，请确保你已安装了 OpenAI 开源的快速分词工具 tiktoken 包
# pip install tiktoken
question = "什么是prompt engineering?"
docs = vectordb.similarity_search(question,k=3)
print(f"检索到的内容数：{len(docs)}")
```

打印检索内容

```python
for i, doc in enumerate(docs):
    print(f"检索到的第{i}个内容: \n {doc.page_content}", end="\n-----------------------------------------------------\n")
```

### 创建LLM实例并构建检索问答链

!!!**说明**
    需要使用LangChain初始化一个LLM实例
    可以参考[LangChainOpenAI.ipynb](../Code/LangChainOpenAI.ipynb)的内容创建一个ChatGPT实例或者Kimi实例

```python
from langchain.prompts import PromptTemplate

template = """使用以下上下文来回答最后的问题。如果你不知道答案，就说你不知道，不要试图编造答
案。最多使用三句话。尽量使答案简明扼要。总是在回答的最后说“谢谢你的提问！”。
{context}
问题: {question}
"""

QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context","question"],
                                 template=template)

```

再创建一个基于模板的检索链

```python
from langchain.chains import RetrievalQA

qa_chain = RetrievalQA.from_chain_type(llm,
                                       retriever=vectordb.as_retriever(),
                                       return_source_documents=True,
                                       chain_type_kwargs={"prompt":QA_CHAIN_PROMPT})

```

对于方法 `RetrievalQA.from_chain_type()` 来说, 如下参数是可选的

* `llm`: 使用的LLM大模型
* `chain_type`: 值可选  `map_reduce`, 也可以利用 `load_qa_chain()` 方法指定
* `chain_type_kwargs`: 自定义的 `prompt`, 格式为 `{"prompt": PROMPT}`
* `return_source_documents`: 是否返回源文档, 也可以使用 `RetrievalQAWithSourceChain()` 方法, 返回源文档的引用
