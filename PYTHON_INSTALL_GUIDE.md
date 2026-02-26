# Python 3.11.14 安装指南

**目标**: 配置 Python 3.11.14 环境，安装项目依赖，启动服务

---

## 📋 当前状态

- ✅ Python 3.11.14 源代码已下载
  - 路径：`E:\Download\Python-3.11.14`
  - 类型：源代码（不是安装程序）

⚠️ **问题**：从源代码安装需要 C 编译器和相关工具，比较复杂。

---

## 🎯 推荐方案：下载 Windows 安装程序

### 方案 A：官方安装程序（推荐，最快）

#### 步骤 1: 下载安装程序

访问以下链接下载 Python 3.11.14 的 Windows 安装程序：

```
https://www.python.org/ftp/python/3.11.14/python-3.11.14-amd64.exe
```

或者访问 Python 官网下载页面：
```
https://www.python.org/downloads/release/python-31114/
```

选择：
- **Windows installer (64-bit)**: `python-3.11.14-amd64.exe`

#### 步骤 2: 安装 Python 3.11.14

1. 双击 `python-3.11.14-amd64.exe`
2. **重要**：勾选 "Add Python 3.11 to PATH"
3. 点击 "Install Now" 或 "Customize installation"
4. 等待安装完成

#### 步骤 3: 验证安装

```powershell
# 在新的 PowerShell 或 CMD 中运行
python --version

# 预期输出：
# Python 3.11.14
```

#### 步骤 4: 创建虚拟环境

```powershell
# 进入项目目录
cd E:\workspace\mPower_Rag

# 创建虚拟环境
python -m venv venv311

# 激活虚拟环境
.\venv311\Scripts\Activate

# 验证虚拟环境
python --version
# 应该显示：Python 3.11.14
```

#### 步骤 5: 安装依赖

```powershell
# 确保虚拟环境已激活（前面有 (venv311) 标记）

# 安装依赖
pip install -r requirements.txt

# 注意：部分包可能会因为 Python 版本兼容性被跳过
```

#### 步骤 6: 启动服务

```powershell
# 终端 1：启动 Qdrant（如果 Docker 已启动）
docker-compose up -d qdrant

# 终端 2：启动 FastAPI
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 3：启动 Streamlit
streamlit run frontend/app.py --server.port 8501
```

---

### 方案 B：使用 Conda（推荐，方便管理）

#### 步骤 1: 安装 Miniconda 或 Anaconda

如果已经安装 Anaconda 或 Miniconda，跳过此步骤。

下载 Miniconda：
```
https://docs.conda.io/en/latest/miniconda.html
```

#### 步骤 2: 创建 Python 3.11.14 环境

```powershell
# 创建新环境
conda create -n mpower_rag python=3.11.14 -y

# 激活环境
conda activate mpower_rag

# 验证版本
python --version
# 应该显示：Python 3.11.14
```

#### 步骤 3: 进入项目目录并安装依赖

```powershell
cd E:\workspace\mPower_Rag

# 安装依赖
pip install -r requirements.txt
```

#### 步骤 4: 启动服务

同方案 A 的步骤 6。

---

### 方案 C：从源码安装（复杂，不推荐）

**警告**：此方案需要 C 编译器和相关工具，比较复杂。

#### 前置要求

需要安装以下工具：
- Visual Studio Build Tools
- C 编译器
- 相关依赖库

#### 安装步骤

```powershell
cd E:\Download\Python-3.11.14

# 配置
./configure --prefix=E:\Python311

# 编译（可能需要很长时间）
make

# 安装
make install
```

**不推荐**，除非你需要自定义编译选项。

---

## ✅ 验证清单

完成安装后，检查以下项目：

- [ ] Python 版本为 3.11.14
- [ ] 可以创建虚拟环境
- [ ] 可以激活虚拟环境
- [ ] 可以安装依赖包
- [ ] 可以运行 Python 脚本

---

## 🚀 快速启动（方案 A 推荐）

```powershell
# 1. 下载并安装 Python 3.11.14
# 从 https://www.python.org/ftp/python/3.11.14/python-3.11.14-amd64.exe 下载

# 2. 创建虚拟环境
cd E:\workspace\mPower_Rag
python -m venv venv311
.\venv311\Scripts\Activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务（需要 Docker 已启动）
docker-compose up -d qdrant
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
streamlit run frontend/app.py --server.port 8501
```

---

## 🆘 遇到问题？

### 问题 1: Python 版本不对
**解决**：确保安装的是 Python 3.11.14，不是其他版本

### 问题 2: 无法安装依赖
**解决**：
1. 升级 pip：`python -m pip install --upgrade pip`
2. 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

### 问题 3: 虚拟环境激活失败
**解决**：
- PowerShell: `.\venv311\Scripts\Activate`
- CMD: `venv311\Scripts\activate.bat`

### 问题 4: Docker 未启动
**解决**：先启动 Docker Desktop

---

## 📞 下一步

安装完成后，告诉我：
1. Python 是否安装成功
2. 虚拟环境是否创建成功
3. 依赖是否安装成功

然后我将帮你：
1. 启动服务
2. 测试对话功能
3. 测试重排序功能

---

**创建时间**: 2026-02-23 16:25
**文档版本**: 1.0
