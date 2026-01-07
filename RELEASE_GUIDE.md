# 发布指南

本指南介绍如何将 `dtrade` 包打包并发布到 PyPI。

## 1. 准备工作

确保安装了最新版本的 `setuptools`, `wheel` 和 `twine`：

```bash
pip install --upgrade setuptools wheel twine
```

## 2. 生成分发包

在项目根目录（包含 `setup.py` 的目录）运行：

```bash
python setup.py sdist bdist_wheel
```

这将生成 `dist/` 目录，其中包含：
- 源码包 (`.tar.gz`)
- 预编译包 (`.whl`)

## 3. 检查包

在上传之前，可以使用 `twine` 检查包文件是否符合 PyPI 标准：

```bash
twine check dist/*
```

## 4. 上传到 PyPI

**注意**：您需要先在 [PyPI](https://pypi.org/) 注册账号。

### 上传到 TestPyPI (推荐用于测试)

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

验证上传成功后，可以尝试从 TestPyPI 安装：

```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps dtrade-python
```

### 上传到正式 PyPI

```bash
twine upload dist/*
```

上传成功后，全世界的用户都可以通过以下命令安装：

```bash
pip install dtrade-python
```

## 5. 版本更新

每次发布新版本前，请务必修改 `setup.py` 中的 `version` 字段。
