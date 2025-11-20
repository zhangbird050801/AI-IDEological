# AI-IDEological 系统快速启动指南

## 🚀 快速启动

### 1. 环境准备

确保你的系统已安装：
- Python 3.11+
- Node.js 18.8.0+
- pnpm (推荐) 或 npm

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd AI-IDEological
```

### 3. 后端设置

#### 方式一：使用MySQL（推荐）

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 准备MySQL数据库
# 登录MySQL创建数据库：
# CREATE DATABASE AIdata CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 5. 初始化数据库
python init_mysql.py
```

#### 方式二：使用SQLite（简单）

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python init_db.py
```

### 4. 前端设置

```bash
# 进入前端目录
cd web

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

### 5. 启动后端服务

```bash
# 回到项目根目录
cd ..

# 启动后端服务
python run.py
```

### 6. 访问系统

- 前端地址：http://localhost:3000
- 后端API文档：http://localhost:9999/docs
- 默认管理员账号：**admin** / **123456**

## 📝 配置说明

### 环境变量配置

在项目根目录创建 `.env` 文件：

```env
# DeepSeek API配置 (必须)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 数据库配置 (如使用MySQL)
DATABASE_URL=mysql://root:root@localhost:3306/AIdata

# 可选配置
DEEPSEEK_API_BASE=https://api.deepseek.com
AIGC_MODEL=deepseek-chat
AIGC_TIMEOUT=60000
```

### MySQL配置说明

如果使用MySQL数据库：

1. **安装MySQL**：
   ```bash
   # macOS
   brew install mysql
   # Ubuntu/Debian
   sudo apt-get install mysql-server
   # CentOS/RHEL
   sudo yum install mysql-server
   ```

2. **启动MySQL服务**：
   ```bash
   # macOS
   brew services start mysql
   # Linux
   sudo systemctl start mysql
   ```

3. **创建数据库**：
   ```sql
   CREATE DATABASE AIdata CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

4. **安装Python MySQL驱动**：
   ```bash
   pip install pymysql
   # 或者使用异步版本
   pip install aiomysql
   ```

### 数据库配置

系统默认使用SQLite数据库，无需额外配置。如需使用MySQL，请修改 `app/settings/config.py` 文件。

## 🔧 常见问题解决

### 问题1：导入错误

如果遇到导入错误，请运行：

```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 确保激活了虚拟环境
source venv/bin/activate
```

### 问题2：数据库初始化失败

```bash
# 删除现有数据库文件（如果存在）
rm -f db.sqlite3

# 重新运行初始化
python init_db.py
```

### 问题3：端口占用

```bash
# 检查端口占用
lsof -i :3000  # 前端端口
lsof -i :9999  # 后端端口

# 杀死占用端口的进程
kill -9 <PID>
```

### 问题4：DeepSeek API密钥

1. 访问 https://platform.deepseek.com/
2. 注册并获取API密钥
3. 在 `.env` 文件中配置密钥

## 📋 功能检查清单

启动成功后，请验证以下功能：

- [ ] 登录系统 (admin/123456)
- [ ] AIGC对话生成
- [ ] 案例库管理
- [ ] 提示词模板管理
- [ ] 教学资源管理
- [ ] 用户管理
- [ ] 角色权限管理

## 🛠️ 开发模式

### 后端开发

```bash
# 启动后端（开发模式）
python run.py

# 查看API文档
# 访问 http://localhost:9999/docs
```

### 前端开发

```bash
# 启动前端（开发模式）
cd web
pnpm dev

# 构建生产版本
pnpm build
```

### 数据库迁移

如需修改数据库结构：

```bash
# 初始化迁移
aerich init -t app.settings.TORTOISE_ORM

# 创建迁移文件
aerich migrate

# 应用迁移
aerich upgrade
```

## 📚 更多文档

- [详细使用指南](docs/CURRICUM_IDEOLOGICAL_GUIDE.md)
- [API文档](http://localhost:9999/docs) (启动后端后访问)
- [系统架构说明](docs/ARCHITECTURE.md)

## 🆘 获取帮助

如果遇到问题：

1. 检查本文档的常见问题部分
2. 查看GitHub Issues
3. 确认依赖版本正确
4. 检查网络连接和API密钥

---

🎉 **恭喜！你已经成功启动了AI-IDEological系统！**