# 0xC0FFee 代码笔记

困了就去补充一杯咖啡因 ^ ^

## 对`@root_validator()`装饰器的理解

```python
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

```

在这段代码中，`@root_validator()` 装饰器的作用是对模型中的字段（特别是 `client` 字段）进行额外的验证或处理。具体来说，它做了以下几件事情：

### 1. 装饰 `validate_environment` 方法

* `@root_validator()` 装饰器在这里包装了 `validate_environment` 方法，使得它在 `BaseModel` 的字段验证完成后执行。
* 默认情况下，`@root_validator(pre=False)` 会在所有字段的验证之后运行，因此，`validate_environment` 这个方法会在模型的字段初步验证完成后调用。

### 2. 客户端实例化

* `validate_environment` 方法的目的是在模型实例化时，检查或设置 `client` 字段的值。
* 它从 `zhipuai` 库中导入 `ZhipuAI` 类，并将 `values["client"]` 设置为 `ZhipuAI` 的一个实例。
* 换句话说，如果用户没有手动提供 `client`，那么这个验证器会自动将 `client` 字段赋值为 `ZhipuAI()` 的一个实例。

### 3. 处理潜在的模块缺失错误

* 如果环境中没有安装 `zhipuai` 库，导入 `ZhipuAI` 会失败，并抛出 `ModuleNotFoundError` 错误。这种情况下，用户将得到明确的错误信息："No module named 'zhipuai'"，提示他们需要安装该库。
* 这种设计可以确保当用户尝试使用 `ZhipuAIEmbeddings` 模型时，必须在环境中正确安装了 `zhipuai` 依赖，否则会导致模型初始化失败。

### 4. 返回修改后的 `values`

* 在 `validate_environment` 方法的最后，经过处理后的 `values` 会被返回。这里的 `values` 是一个字典，包含了模型的所有字段（此处主要是 `client`），经过验证和实例化后，最终返回给模型实例。
* 返回的 `values` 确保字段 `client` 始终是一个有效的 `ZhipuAI` 实例。

### 代码执行流程分析

1. 模型实例化：
   当创建 `ZhipuAIEmbeddings` 的实例时，`BaseModel` 负责首先验证所有字段的类型和数据有效性。

2. `root_validator` 执行：
   字段验证完成后，`@root_validator()` 会触发 `validate_environment` 方法，检查或设置 `client` 字段。

3. 实例化 `client` 字段：
   在 `validate_environment` 方法中，`ZhipuAI` 被导入并实例化为 `values["client"]`，确保 `client` 字段始终是一个有效的 `ZhipuAI` 对象。

4. 返回修改后的 `values`：
   修改后的 `values`（包含 `client` 字段的实例化值）将返回给模型，确保后续代码能够正常使用这个已经初始化好的 `client`。

### 总结 `@root_validator()` 的作用

在这个上下文中，`@root_validator()` 的作用是确保模型中的 `client` 字段被正确实例化为 `ZhipuAI` 类的一个对象。如果环境中没有安装 `zhipuai` 库，代码会抛出一个导入错误。这个装饰器的主要目的是在数据模型实例化时，进行额外的逻辑验证和处理，以确保模型的依赖项（如 `client` 字段）在运行时是可用且已正确初始化的。

## `client`不是字典`values`中的一个 Key 吗？为什么能通过self直接调用呢

这是因为 Pydantic 的 BaseModel 在内部会自动处理这个转换过程。让我详细解释下：

### 1. 在类定义时，我们声明了 client 作为类的属性

```python
class ZhipuAIEmbeddings(BaseModel, Embeddings):
    client: Any  # 这里声明了 client 作为类的属性
```

### 2. 当使用 @root_validator 时，我们确实是在操作 values 字典

```python
@root_validator()
def validate_environment(cls, values: Dict) -> Dict:
    values["client"] = ZhipuAI()  # 将值存入字典
    return values
```

### 3. Pydantic 的 BaseModel 会自动将 values 字典中的值映射到类的属性上。这是 Pydantic 的一个核心特性。它会

* 接收 validate_environment 返回的 values 字典
* 找到字典中的 "client" 键
* 将对应的值自动设置为实例的 self.client 属性

所以虽然我们在验证器中使用字典操作，但 Pydantic 会自动将其转换为实例属性，使得我们可以通过 self.client 来访问。

这个过程可以类比为：

```python
# Pydantic 在内部大致进行这样的操作
class ZhipuAIEmbeddings:
    def __init__(self):
        values = self.validate_environment({})  # 调用验证器
        self.client = values["client"]  # 将字典值转换为实例属性
```

这就是为什么我们可以在 embed_query 方法中直接使用 self.client 的原因。

## 在pydantic v1中，可以使用@root_validator()来实现client实例初始化，但是@model_validator()为什么就不支持了呢？

你提到的区别与 Pydantic v2 中的设计更改有关。**`@model_validator`** 是 Pydantic v2 中的新特性，而 **`@root_validator`** 是 Pydantic v1 中的特性。Pydantic v2 做了一些架构上的更改，导致它们的行为有所不同。下面是详细的解释：

### 1. **Pydantic v1 (`@root_validator`)**

在 Pydantic v1 中，`@root_validator` 是用于在所有字段验证完成后，执行一些额外的验证逻辑或修改字段值。它允许你修改整个模型的字段，并且返回修改后的字段字典。

```python
from pydantic import BaseModel, root_validator

class ZhipuAIEmbeddings(BaseModel):
    client: Optional[Any] = None

    @root_validator(pre=False)
    def validate_environment(cls, values: Dict) -> Dict:
        if values["client"] is None:
            from zhipuai import ZhipuAI
            values["client"] = ZhipuAI()  # 修改 values 字典
        return values
```

在这个例子中，`@root_validator` 能够正确修改 `values` 字典，并将其返回。这是 Pydantic v1 的典型用法。

### 2. **Pydantic v2 (`@model_validator`)**

在 Pydantic v2 中，`@root_validator` 被替换为 **`@model_validator`**，并且验证的机制有了一些变化。`@model_validator` 的设计是为了让校验逻辑更明确、严格，避免一些在 v1 中可能导致混淆的行为。尤其是在字段的修改上，v2 更加严谨。

**关键区别**是，Pydantic v2 不再允许直接修改 `values`，同时它引入了两种验证模式：**before** 和 **after**。

- **before** 模式：字段验证之前运行。
- **after** 模式：字段验证之后运行。

在 `after` 模式下，Pydantic v2 期望验证器返回的不是修改后的字典，而是一个经过验证的对象。你不能像在 v1 中那样直接修改 `values` 字典，因为 v2 的 `@model_validator` 旨在更严格地保护模型字段的完整性和不变性。

例如，你的代码中：

```python
@model_validator(mode="after")
def validate_environment(cls, values: Dict) -> Dict:
    if values["client"] is None:
        from zhipuai import ZhipuAI
        values["client"] = ZhipuAI()  # 直接修改 values 是不允许的
    return values
```

在 v2 中，Pydantic 不允许直接修改 `values`。你需要返回一个新的对象或者使用 `setattr` 来修改实例字段。

### 解决方案

在 Pydantic v2 中，如果你需要在字段验证之后进行某些额外的初始化或修改，比如实例化 `client`，你可以使用 `setattr` 或者直接在 `__init__` 中处理。

#### 1. 使用 `setattr` 修改字段

```python
@model_validator(mode="after")
def validate_environment(cls, values: Dict) -> Dict:
    if values["client"] is None:
        from zhipuai import ZhipuAI
        setattr(cls, "client", ZhipuAI())  # 使用 setattr 修改字段
    return values
```

#### 2. 使用 `__init__` 方法

在 Pydantic v2 中，更推荐使用 `__init__` 方法来处理类似的初始化逻辑，因为它更符合 Pydantic v2 的设计哲学：

```python
class ZhipuAIEmbeddings(BaseModel, Embeddings):
    client: Optional[Any] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.client is None:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI()  # 初始化 client
```

### 总结

- 在 **Pydantic v1** 中，`@root_validator` 允许你直接修改 `values` 字典，这使得修改字段的方式非常灵活。
- 在 **Pydantic v2** 中，`@model_validator` 的行为更加严格，不允许直接修改 `values`。你需要使用 `setattr` 或者在 `__init__` 方法中进行初始化。

这是 Pydantic v2 为了增强数据模型的安全性和一致性而做出的设计决策。
