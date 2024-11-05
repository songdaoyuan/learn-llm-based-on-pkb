# 0x02 LLM API详细用法的实例

## 基础概念的导入

### 1. Prompt

Prompt是NLP中为特定任务设计的输入模板，每种任务对应一种Prompt。

ChatGPT推广后，Prompt 开始被推广为给大模型的所有输入，而模型返回的输出称为Completion。

### 2. Temperature

LLM生成结果具有随机性，通过调整顶层预测概率生成最终输出。

Temperature参数（0-1）控制随机性：值低时文本保守可预测，值高时文本更具创造性和多样性。在个人知识库助手场景中设为0以确保稳定性，避免错误；

### 3. System Prompt

System Prompt是GPT API中用于持久影响模型回复的设置，与普通User Prompt相比具有更高重要性。它用于初始化模型，如设定人设，而User Prompt则是模型回复的具体输入。

在会话中，System Prompt一般只有一个，用于设定模型的初始状态，之后通过User Prompt给出具体指令。

```json
{
    "system prompt": "你是一个幽默风趣的个人知识库助手，可以根据给定的知识库内容回答用户的提问，注意，你的回答风格应是幽默风趣的",
    "user prompt": "如何部署基于PLG的日志服务？"
}
```

## 使用 ChatGPT / Kimi

