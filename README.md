# 视频观看实验平台 (Video Viewing Experiment Platform)

基于 Flask 的学术研究视频实验平台，用于研究用户的视频观看行为。

## 项目结构 (Project Structure)

```
vedioproject/
├── app.py                  # Flask 主应用程序（路由和请求处理）
├── config.py              # 配置文件（常量和设置）
├── database.py            # 数据库操作模块
├── video_loader.py        # 视频加载和播放列表管理
├── session_manager.py     # 会话管理工具
├── utils.py               # 统计计算工具
├── view_database.py       # 数据库查看工具
├── requirements.txt       # Python 依赖包
├── douyin_videos.xlsx     # 视频元数据
├── .env / 环境变量配置      # PostgreSQL 连接（DATABASE_URL）
├── douyin_videos/         # 本地视频文件目录
├── static/
│   ├── css/
│   │   └── style.css     # 全局样式
│   └── videos/           # （预留）
└── templates/
    ├── welcome.html       # 欢迎页面
    ├── categories.html    # 分类选择页面
    ├── play_video.html    # 视频播放页面
    └── summary.html       # 统计总结页面
```

## 代码模块说明 (Module Description)

### app.py (主应用)
Flask 应用的主文件，包含所有路由和请求处理：
- `/` - 欢迎页面，初始化用户会话
- `/categories` - 分类选择页面
- `/select_categories` - 处理分类选择，生成播放列表
- `/play_video/<index>` - 视频播放页面
- `/like_video` - 处理点赞/点踩
- `/add_comment` - 添加评论
- `/save_watch_duration` - 保存观看时长
- `/summary` - 显示统计总结

### config.py (配置管理)
集中管理所有配置常量：
- Flask 配置（密钥、调试模式、主机、端口）
- 数据库配置（路径、超时设置）
- 文件路径（Excel、视频目录）
- 分类映射（中文 → Excel 分类）
- 视频分配规则（每轮的视频数量）

### database.py (数据库层)
提供数据库操作的封装：
- `get_db_connection()` - 上下文管理器，自动提交/回滚
- `init_db()` - 初始化数据库表
- `save_category_selection()` - 保存用户分类选择
- `save_watch_log()` - 保存视频观看记录
- `get_session_statistics()` - 查询会话统计数据

### video_loader.py (视频管理)
处理视频加载和播放列表生成：
- `VideoLoader` 类封装视频加载逻辑
- 从 Excel 读取视频元数据
- 验证本地视频文件是否存在
- 根据用户选择和轮次生成播放列表
- 支持随机打乱视频顺序

### session_manager.py (会话管理)
Flask 会话操作的工具函数：
- `initialize_session()` - 初始化新用户会话
- `get_user_info()` - 获取当前用户信息
- `update_likes()` - 更新点赞状态
- `add_comment()` - 添加评论
- `calculate_watch_stats()` - 计算观看统计数据
- `increment_round()` - 递增实验轮次

### utils.py (工具函数)
通用工具和统计计算：
- `calculate_summary_statistics()` - 计算总结统计数据
- 格式化时间（分钟和秒）
- 计算百分比分布
- 数据排序和聚合

## 功能特点 (Features)

### ✅ 双轮实验设计
- **第一轮**：20 个视频（10-6-4 分配）
- **第二轮**：6 个视频（2-2-2 分配）

### ✅ 智能分类选择
- 9 个视频分类，用户选择 3 个
- 滑块式评分界面（0-10 分）
- 自动锁定机制

### ✅ 本地视频播放
- HTML5 视频播放器
- 支持 MP4 格式
- 自动播放下一个视频
- 前进/后退导航

### ✅ 用户行为追踪
- 观看时长记录
- 完成率计算
- 点赞/点踩统计
- 评论收集

### ✅ 数据持久化
- PostgreSQL 数据库
- 两张表：用户选择 + 观看记录
- 按轮次分离数据

### ✅ 可视化报告
- 观看统计总结
- Chart.js 饼图
- 分类时长分布
- 实验完成提示

### ✅ 代码质量
- 模块化架构
- 清晰的职责分离
- 完善的错误处理
- 上下文管理器
- 类型安全

## 安装和运行 (Installation & Running)

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置数据库连接
设置环境变量 `DATABASE_URL`（示例）：

```bash
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/user_behavior
```

### 3. 准备视频文件
- 将 MP4 文件放在 `douyin_videos/` 目录
- 文件名格式：`{video_id}.mp4`
- 确保与 Excel 中的 ID 匹配

### 4. 运行应用
```bash
python app.py
```

### 5. 访问平台
在浏览器打开：`http://localhost:5000`

## 视频分类 (Categories)

- 日常生活记录(vlog) - Daily Life Vlogs
- 服装穿搭 - Fashion & Dressing
- 运动健身 - Sports & Fitness
- 美食烹饪 - Gourmet & Cooking
- 发型 - Hairstyles
- 自制饮料 - Homemade Drinks
- 孩童 - Kids
- 音乐现场 - Live Music
- 化妆美容 - Makeup & Beauty

## 数据库表结构 (Database Schema)

### user_selections
记录用户的分类选择：
- user_id, session_id
- category_1/2/3 及对应评分
- timestamp

### video_watch_log
记录视频观看数据：
- user_id, session_id, round
- video_id, title, category
- watch_duration, completion_rate
- liked, comment
- timestamp

## 查看数据 (View Data)

使用 `view_database.py` 查看或导出数据：

```bash
python view_database.py
```

选项：
1. 查看用户分类选择
2. 查看视频观看记录
3. 导出到 Excel

## 技术栈 (Tech Stack)

- **后端**：Flask 3.0.0
- **数据库**：PostgreSQL
- **数据处理**：pandas 2.1.4
- **前端**：HTML5, CSS3, JavaScript
- **图表**：Chart.js
- **Python**：3.8+

## 开发特性 (Development Features)

- 模块化代码结构
- 上下文管理器保证资源释放
- 错误处理和日志记录
- 会话管理和状态追踪
- 每次实验唯一 ID
- 支持并发请求（带超时）

## License

This project is for academic research purposes.
