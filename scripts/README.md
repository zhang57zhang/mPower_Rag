# 开发脚本使用指南

本目录包含 mPower_Rag 项目的开发和部署脚本。

---

## 📋 脚本列表

### 初始化脚本

#### `setup.bat` (Windows)
初始化开发环境（Windows）

```bash
setup.bat
```

功能：
- 创建虚拟环境
- 安装 Python 依赖
- 创建必要的目录
- 生成 .env 文件

#### `setup.sh` (Linux/Mac)
初始化开发环境（Linux/Mac）

```bash
chmod +x setup.sh
./setup.sh
```

功能：同上

---

### 恢复脚本

#### `resume.bat` (Windows)
恢复开发环境并显示进度（Windows）

```bash
resume.bat
```

功能：
- 读取 PROGRESS.md
- 显示当前进度
- 显示下一步任务
- 提供恢复提示

#### `resume.py` (跨平台)
恢复开发环境并显示进度（Python）

```bash
python scripts/resume.py
```

功能：同上

---

### 环境检查脚本

#### `check.bat` (Windows)
检查开发环境（Windows）

```bash
check.bat
```

功能：
- 检查 Python 版本
- 检查依赖包
- 检查环境变量
- 检查项目结构
- 检查外部服务（Qdrant）

#### `check.py` (跨平台)
检查开发环境（Python）

```bash
python scripts/check.py
```

功能：同上

---

## 🚀 典型工作流

### 首次设置

1. **克隆项目**
   ```bash
   git clone <repo-url>
   cd mPower_Rag
   ```

2. **运行初始化脚本**
   ```bash
   # Windows
   scripts\setup.bat

   # Linux/Mac
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **配置环境变量**
   ```bash
   # 编辑 .env 文件
   # 填入 LLM_API_KEY 等必要配置
   ```

4. **启动服务**
   ```bash
   # 使用 Docker Compose（推荐）
   docker-compose up -d

   # 或手动启动
   python src/api/main.py
   streamlit run frontend/app.py
   ```

### 每天开始工作

1. **检查环境**
   ```bash
   # Windows
   scripts\check.bat

   # Linux/Mac
   python scripts/check.py
   ```

2. **恢复进度**
   ```bash
   # Windows
   scripts\resume.bat

   # Linux/Mac
   python scripts/resume.py
   ```

3. **继续开发**
   - 查看 TODO.md
   - 查看当前优先级任务
   - 开始开发

### 测试更改

1. **停止服务**（如果运行中）
   ```bash
   docker-compose down
   ```

2. **应用更改**
   - 修改代码
   - 安装新依赖（如需要）
   - 更新配置

3. **重启服务**
   ```bash
   docker-compose up -d
   ```

4. **验证功能**
   - 访问前端: http://localhost:8501
   - 访问 API: http://localhost:8000
   - 查看日志: docker-compose logs -f

---

## 📝 脚本维护

### 添加新脚本

1. 创建脚本文件
2. 添加适当的 Shebang（Linux/Mac）
3. 添加 Windows 批处理包装（如需要）
4. 更新本文档
5. 测试脚本

### 脚本规范

- **Python 脚本**:
  - 使用 Python 3.10+ 语法
  - 添加类型注解
  - 添加文档字符串
  - 处理异常
  - 返回适当的退出码

- **批处理脚本**:
  - 使用 `echo` 输出信息
  - 使用 `pause` 在关键步骤等待
  - 检查错误 (`errorlevel`)
  - 提供清晰的错误信息

---

## 🔍 故障排除

### 脚本无法执行

**问题**: `permission denied`

**解决**:
```bash
chmod +x scripts/setup.sh
```

### Python 未找到

**问题**: `python: command not found`

**解决**:
- 确保 Python 3.10+ 已安装
- 添加 Python 到 PATH
- 或使用完整路径: `/usr/bin/python3`

### 依赖安装失败

**问题**: `pip install failed`

**解决**:
- 升级 pip: `pip install --upgrade pip`
- 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple`
- 检查网络连接

### Docker 相关问题

**问题**: Docker 命令失败

**解决**:
- 确保 Docker 已安装并运行
- 检查 Docker Daemon 状态: `docker ps`
- 重启 Docker 服务

---

## 📚 相关文档

- [项目根目录](../README.md) - 项目说明
- [快速开始](../docs/QUICKSTART.md) - 快速开始指南
- [开发进度](../PROGRESS.md) - 详细进度跟踪
- [任务清单](../TODO.md) - 待办任务

---

**最后更新**: 2026-02-22
