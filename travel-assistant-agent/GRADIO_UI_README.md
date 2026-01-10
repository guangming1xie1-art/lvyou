# 🌍 智能旅行助手 - Gradio聊天界面

基于Gradio的智能旅行助手聊天界面，支持多媒体交互，让用户通过纯对话方式与AI助手交互完成旅行规划。

## ✨ 特性

### 🤖 Agent工作流程
- **🔍 信息收集**：逐步收集用户偏好（目的地、日期、预算、兴趣等）
- **🔎 搜索比较**：搜索航班、酒店等选项并进行比较
- **💡 智能推荐**：基于搜索结果提供个性化推荐和详细信息
- **📋 预订确认**：处理预订相关事务和确认

### 🎨 多媒体支持
- **💬 文字对话**：自然语言交互
- **🖼️ 图片上传**：目的地图片、景点照片等
- **🎵 语音录入**：语音输入旅行需求
- **🎬 视频文件**：旅游视频、景点视频等
- **📱 响应式界面**：适配不同设备

### 🎯 智能功能
- **状态管理**：维护对话状态和Agent流程进度
- **错误处理**：用户友好的错误提示
- **进度显示**：实时显示当前处理阶段
- **历史记录**：完整保留对话历史

## 🚀 快速开始

### 1. 环境准备

确保已安装：
- Python 3.10+
- 旅行助手Agent项目依赖

### 2. 安装依赖

```bash
cd travel-assistant-agent

# 安装Gradio界面依赖
pip install -r requirements-gradio.txt

# 或者安装所有依赖
pip install -r requirements.txt
```

### 3. 启动应用

```bash
# 一键启动
python run_gradio.py

# 或者直接启动
python -m src.gradio_ui.app
```

应用将在 `http://localhost:7860` 启动。

### 4. 访问界面

打开浏览器访问：`http://localhost:7860`

## 📖 使用指南

### 基本交互流程

1. **开始对话**
   - 系统会显示欢迎消息和功能介绍
   - 输入您的旅行需求

2. **信息收集阶段**
   - Agent会逐步询问：
     - 目的地
     - 出行日期和天数
     - 预算范围
     - 偏好类型（美食、自然、文化等）

3. **搜索阶段**
   - Agent搜索相关信息：
     - 景点推荐
     - 酒店选项
     - 交通信息
     - 天气情况

4. **推荐阶段**
   - 生成个性化推荐：
     - 行程安排
     - 预算估算
     - 亮点推荐

5. **预订阶段**
   - 处理预订事务：
     - 确认选择
     - 处理支付
     - 预订详情

### 多媒体交互

#### 图片上传
- 支持格式：JPG, PNG, GIF, BMP, WebP
- 最大大小：50MB
- 用途：上传目的地图片、参考照片等

#### 语音输入
- 支持格式：MP3, WAV, M4A, AAC, OGG
- 最大大小：50MB
- 用途：语音描述旅行需求

#### 视频文件
- 支持格式：MP4, AVI, MOV, WMV, FLV, WebM
- 最大大小：50MB
- 用途：上传旅游视频、景点介绍等

### 界面说明

#### 左侧聊天区域
- **聊天历史**：显示完整的对话记录
- **输入框**：输入文字消息或描述需求
- **发送按钮**：发送消息
- **清除按钮**：开始新对话
- **文件上传**：支持图片、音频、视频上传

#### 右侧信息面板
- **当前阶段**：显示Agent当前处理阶段
- **收集信息**：展示已收集的旅行偏好
- **进度指示器**：显示整体进度
- **快速提示**：使用建议和帮助

## 🔧 技术实现

### 项目结构

```
travel-assistant-agent/
├── src/
│   └── gradio_ui/
│       ├── __init__.py
│       ├── app.py              # Gradio主应用
│       ├── agent_bridge.py     # Agent桥接层
│       └── utils.py            # 工具函数
├── run_gradio.py               # 启动脚本
└── requirements-gradio.txt     # 依赖文件
```

### 核心组件

#### 1. TravelAssistantApp
- Gradio应用主类
- 界面布局和事件处理
- 用户交互管理

#### 2. AgentBridge
- 连接现有Agent系统
- 消息路由和状态管理
- Agent工作流控制

#### 3. 工具函数
- `process_uploaded_file()`: 文件处理
- `format_agent_response()`: 响应格式化
- `create_multimedia_display()`: 多媒体展示
- `validate_multimedia_file()`: 文件验证

### Agent集成

Gradio界面通过AgentBridge连接到现有的Agent系统：

```
Gradio UI ←→ AgentBridge ←→ InfoCollectionAgent
                       ←→ SearchAgent  
                       ←→ RecommendationAgent
                       ←→ BookingAgent
                       ←→ SkillBasedAgent
```

## 🎮 交互示例

### 示例1：基本旅行规划

```
用户: "我想计划一个东京之旅"
Agent: "很好！请问您想什么时候去？预算大概是多少？"

用户: "3月份，预算5000美元"
Agent: "已记录您的需求。让我为您搜索航班和酒店..."

用户: "推荐最佳套餐"
Agent: "搜索完成！我为您找到了相关信息，现在为您生成个性化推荐..."
```

### 示例2：多媒体交互

```
用户: [上传东京景点图片] "3月份去东京，喜欢文化和美食"
Agent: "收到您的图片！我看到这是东京的景点照片，已记录您的偏好..."
```

### 示例3：语音输入

```
用户: [语音输入] "我想去巴黎旅行，5月份，预算3000欧元"
Agent: "收到您的语音输入！巴黎是个很棒的选择，已为您记录以下信息..."
```

## 🔍 API端点

### 本地API调用

如果您想通过API方式调用Agent功能：

```python
# 调用信息收集Agent
curl -X POST http://localhost:8000/agent/start-planning \
  -H "Content-Type: application/json" \
  -d '{"user_message": "我想去北京旅游3天"}'

# 调用MCP Skills
curl -X POST http://localhost:8000/mcp/call-skill \
  -H "Content-Type: application/json" \
  -d '{"skill_name": "search_destination", "parameters": {"destination": "Tokyo"}}'
```

## 🛠️ 开发指南

### 自定义样式

修改`app.py`中的`_get_custom_css()`方法来自定义界面样式：

```python
def _get_custom_css(self) -> str:
    return """
    .gradio-container {
        /* 自定义样式 */
    }
    """
```

### 添加新的Agent

在`agent_bridge.py`中扩展`_route_to_agent()`方法：

```python
async def _route_to_agent(self, user_message: str) -> Dict[str, Any]:
    if self.current_stage == "custom_stage":
        return await self._handle_custom_stage(user_message)
```

### 扩展文件支持

在`utils.py`中添加新的文件类型验证：

```python
def validate_multimedia_file(file_path: str, file_name: str) -> Tuple[bool, str]:
    # 添加新的文件类型检查
```

## 🐛 故障排除

### 常见问题

1. **启动失败**
   ```
   解决方案：
   - 检查Python版本 (需要3.10+)
   - 安装所有依赖: pip install -r requirements-gradio.txt
   - 检查端口7860是否被占用
   ```

2. **Agent响应慢**
   ```
   解决方案：
   - 检查网络连接
   - 确认Claude API配置正确
   - 查看日志获取详细错误信息
   ```

3. **文件上传失败**
   ```
   解决方案：
   - 检查文件大小 (最大50MB)
   - 确认文件格式支持
   - 检查临时目录权限
   ```

4. **界面显示异常**
   ```
   解决方案：
   - 清除浏览器缓存
   - 尝试刷新页面
   - 检查浏览器兼容性
   ```

### 日志查看

查看详细日志信息：

```bash
# 查看应用日志
tail -f logs/gradio_app.log

# 或者在控制台查看
python run_gradio.py
```

### 调试模式

启用调试模式：

```python
# 在app.py中设置
app.launch(debug=True, show_error=True)
```

## 📋 系统要求

### 最低配置
- Python 3.10+
- 2GB RAM
- 1GB 磁盘空间
- 网络连接

### 推荐配置
- Python 3.11+
- 4GB RAM
- 2GB 磁盘空间
- 稳定的网络连接

### 浏览器支持
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork项目
2. 创建功能分支
3. 提交变更
4. 创建Pull Request

### 代码规范
- 遵循PEP 8
- 添加必要的注释
- 确保代码可读性
- 添加单元测试

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🆘 支持

如果您遇到问题或需要帮助：

1. 查看本文档的故障排除部分
2. 搜索已知的Issues
3. 创建新的Issue描述问题
4. 联系开发团队

---

🌟 **享受您的智能旅行规划之旅！** ✈️🗺️🌍