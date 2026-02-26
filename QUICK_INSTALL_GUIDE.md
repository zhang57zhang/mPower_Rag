# 快速安装指南 - Python 3.11.9

**时间**: 2026-02-23 16:42
**安装程序**: `E:\Download\python-3.11.9\python-3.11.9-amd64.exe`

---

## ✅ 快速安装（5 分钟）

### 步骤 1: 安装 Python 3.11.9

```powershell
# 1. 双击运行安装程序
E:\Download\python-3.11.9\python-3.11.9-amd64.exe

# 2. 重要：勾选 "Add Python 3.11 to PATH"
# 3. 点击 "Install Now"
# 4. 等待安装完成（约 2-3 分钟）
```

### 步骤 2: 验证安装

```powershell
# 打开新的 PowerShell 或 CMD
python --version

# 预期输出：
# Python 3.11.9
```

### 步骤 3: 创建虚拟环境

```powershell
# 进入项目目录
cd E:\workspace\mPower_Rag

# 创建虚拟环境
python -m venv venv311

# 激活虚拟环境
.\venv311\Scripts\Activate

# 验证（应该看到 (venv311) 前缀）
python --version
```

### 步骤 4: 安装依赖

```powershell
# 确保虚拟环境已激活（有 (venv311) 前缀）

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 注意：部分包可能会跳过（注释掉了不兼容的包）
```

### 步骤 5: 启动服务

```powershell
# 终端 1：启动 Qdrant（需要 Docker）
docker-compose up -d qdrant

# 终端 2：启动 FastAPI（新终端，激活虚拟环境）
cd E:\workspace\mPower_Rag
.\venv311\Scripts\Activate
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 3：启动 Streamlit（新终端，激活虚拟环境）
cd E:\workspace\mPower_Rag
.\venv311\Scripts\Activate
streamlit run frontend/app.py --server.port 8501
```

### 步骤 6: 访问服务

```
前端: http://localhost:8501
API:  http://localhost:8000
API 文档: http://localhost:8000/docs
```

---

## 🔧 安装后检查

### Python 版本

```powershell
python --version
# 应该显示：Python 3.11.9
```

### 虚拟环境

```powershell
# 查看虚拟环境目录
dir venv311

# 激活虚拟环境
.\venv311\Scripts\Activate
# 应该看到 (venv311) 前缀
```

### 依赖安装

```powershell
# 查看已安装的包
pip list

# 检查关键包
pip show fastapi
pip show streamlit
pip show qdrant-client
```

### 服务启动

```powershell
# 检查 Qdrant
curl http://localhost:6333/collections

# 检查 API
curl http://localhost:8000/health

# 检查前端
# 访问 http://localhost:8501
```

---

## 🆘 常见问题

### 问题 1: python 命令未找到

**解决方法**：
1. 确保安装时勾选了 "Add Python 3.11 to PATH"
2. 重新打开 PowerShell 或 CMD
3. 重启电脑

### 问题 2: 虚拟环境激活失败

**解决方法**：
```powershell
# PowerShell
.\venv311\Scripts\Activate

# CMD
venv311\Scripts\activate.bat
```

### 问题 3: 依赖安装失败

**解决方法**：
```powershell
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 或者使用阿里云镜像
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 问题 4: Docker 未启动

**解决方法**：
1. 打开 Docker Desktop
2. 等待 Docker 完全启动
3. 然后运行 `docker-compose up -d qdrant`

---

## 📋 完成清单

- [ ] Python 3.11.9 安装完成
- [ ] `python --version` 显示 3.11.9
- [ ] 虚拟环境创建成功
- [ ] 虚拟环境可以激活
- [ ] 依赖包安装完成
- [ ] Qdrant 启动成功
- [ ] FastAPI 启动成功
- [ ] Streamlit 启动成功
- [ ] 可以访问前端 http://localhost:8501
- [ ] 可以访问 API http://localhost:8000

---

## 🚀 一键启动脚本

如果你想一键启动所有服务，运行：

```powershell
# 注意：需要先完成上述安装步骤
scripts\start_all.bat
```

---

## 🎯 完成后

告诉我：
1. ✅ Python 安装成功
2. ✅ 虚拟环境创建成功
3. ✅ 依赖安装成功
4. ✅ 服务启动成功

然后我将帮你：
1. 测试对话功能
2. 测试重排序功能
3. 验证所有功能正常工作

---

**快速参考**：
- 安装程序：`E:\Download\python-3.11.9\python-3.11.9-amd64.exe`
- 项目目录：`E:\workspace\mPower_Rag`
- 虚拟环境：`.\venv311\Scripts\Activate`
- 前端地址：http://localhost:8501
- API 地址：http://localhost:8000

---

**创建时间**: 2026-02-23 16:42
**文档版本**: 1.0
