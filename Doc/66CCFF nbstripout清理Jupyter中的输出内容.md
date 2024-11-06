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

### 3.使用 Git pre-commit 钩子

在 Git 仓库中创建 .git/hooks/pre-commit 文件，并添加如下内容：

```sh
#!/bin/bash
# 清除所有 Jupyter Notebook 的输出
jupyter nbconvert --clear-output --inplace $(git diff --cached --name-only | grep '.ipynb')
```

赋予可执行权限

`chmod +x .git/hooks/pre-commit`

当执行 git commit 时，钩子会自动清除所有已经 staged 的 .ipynb 文件的输出。

### 4.手动使用 nbconvert 清除输出

如果不使用自动化，也可以在提交之前手动执行以下命令来清除输出：

`jupyter nbconvert --clear-output --inplace your_notebook.ipynb`
