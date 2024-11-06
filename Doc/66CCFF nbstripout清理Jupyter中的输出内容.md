# 66CCFF nbstripout清理jupyter中的输出内容

nbstripout 可以清除 Jupyter Notebook 中的输出并且可以集成到 Git 的钩子中，确保每次提交之前都自动执行清理操作。

## 使用方法

### 1.安装

`pip install nbstripout`

### 2.初始化 Git 仓库中的 nbstripout

在 Git 仓库目录下执行以下命令，将 nbstripout 配置为 Git 的钩子，这样每次提交时它会自动清理输出：

`nbstripout --install`

如果你只希望清除某些特定的文件（如 .ipynb 文件），可以使用：

`nbstripout --install --attributes=.gitattributes`

检查 .gitattributes

nbstripout 会自动在你的仓库中创建或更新 .gitattributes 文件，确保其中包含如下内容：

`*.ipynb filter=nbstripout`

这行配置会告诉 Git 使用 nbstripout 过滤器来处理所有 .ipynb 文件。
