# 旅游助手前端应用

智能旅游助手 MVP 前端项目，基于 React + Vite + TypeScript 构建。

## 技术栈

- **React 18** - 前端框架
- **Vite** - 构建工具
- **TypeScript** - 类型安全
- **React Router v6** - 路由管理
- **TanStack Query** - 数据获取和缓存
- **Zustand** - 状态管理
- **Tailwind CSS** - UI 样式框架
- **Axios** - HTTP 客户端
- **Vitest** - 单元测试
- **ESLint + Prettier** - 代码规范

## 项目结构

```
travel-assistant-web/
├── public/                 # 静态资源
├── src/
│   ├── components/        # 组件
│   │   └── common/       # 通用组件
│   ├── hooks/            # 自定义 Hooks
│   ├── pages/            # 页面组件
│   ├── services/         # API 服务
│   ├── store/            # Zustand 状态管理
│   ├── theme/            # 主题配置
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数
│   ├── App.tsx           # 主应用组件
│   ├── main.tsx          # 应用入口
│   ├── router.tsx        # 路由配置
│   └── index.css         # 全局样式
├── tests/                # 测试文件
├── .env.example          # 环境变量示例
├── Dockerfile            # Docker 配置
├── docker-compose.yml    # Docker Compose 配置
└── README.md            # 项目文档
```

## 快速开始

### 前置要求

- Node.js >= 18
- npm >= 9

### 安装依赖

```bash
npm install
```

### 环境配置

复制 `.env.example` 文件为 `.env` 并配置环境变量：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8080/api/v1
VITE_APP_NAME=旅游助手
VITE_ENV=development
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录

### 预览生产版本

```bash
npm run preview
```

## 开发指南

### 代码规范

项目使用 ESLint 和 Prettier 进行代码规范检查：

```bash
# 检查代码规范
npm run lint

# 自动修复代码规范问题
npm run lint:fix

# 格式化代码
npm run format

# 检查代码格式
npm run format:check
```

### 类型检查

```bash
npm run type-check
```

### 运行测试

```bash
# 运行测试
npm run test

# 运行测试 UI
npm run test:ui
```

## Docker 部署

### 构建镜像

```bash
docker build -t travel-assistant-frontend .
```

### 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f
```

应用将在 http://localhost:3000 启动

## API 配置

前端通过环境变量 `VITE_API_BASE_URL` 配置后端 API 地址。开发环境下，Vite 会代理 `/api` 请求到后端服务。

代理配置在 `vite.config.ts` 中：

```typescript
server: {
  proxy: {
    '/api': {
      target: process.env.VITE_API_BASE_URL || 'http://localhost:8080',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '/api/v1')
    }
  }
}
```

## 路由配置

应用路由配置在 `src/router.tsx`：

- `/` - 首页
- `/info-collection` - 信息收集页
- `/plans` - 方案展示页
- `/plans/:id` - 方案详情页
- `/attractions` - 景点美食页
- `/order-confirm` - 订单确认页
- `*` - 404 页面

## 状态管理

项目使用 Zustand 进行状态管理：

### Auth Store

用户认证状态：

```typescript
import { useAuthStore } from '@/store'

const { user, token, isAuthenticated, login, logout } = useAuthStore()
```

### Travel Store

旅游相关状态：

```typescript
import { useTravelStore } from '@/store'

const { currentRequest, plans, selectedPlan, setCurrentRequest, selectPlan } = useTravelStore()
```

## 自定义 Hooks

### useAuth

用户认证相关操作：

```typescript
import { useAuth } from '@/hooks/useAuth'

const { user, isAuthenticated, login, logout, register } = useAuth()
```

### useTravel

旅游相关操作：

```typescript
import { useTravel } from '@/hooks/useTravel'

const { createRequest, usePlansQuery, createOrder } = useTravel()
```

## API 服务

API 服务封装在 `src/services` 目录：

- `authService.ts` - 认证相关 API
- `travelService.ts` - 旅游相关 API
- `api.ts` - API 端点配置

使用示例：

```typescript
import { authService } from '@/services/authService'
import { travelService } from '@/services/travelService'

// 登录
const response = await authService.login({ email, password })

// 创建旅游请求
const request = await travelService.createRequest(data)
```

## 工具函数

### 请求工具

封装了 Axios 实例和拦截器：

```typescript
import { http } from '@/utils/request'

const data = await http.get('/endpoint')
```

### 存储工具

本地存储工具：

```typescript
import { setStorage, getStorage, removeStorage } from '@/utils/storage'

setStorage('key', value)
const value = getStorage('key')
removeStorage('key')
```

### 格式化工具

常用格式化函数：

```typescript
import { formatDate, formatCurrency, formatPhone } from '@/utils/format'

const date = formatDate(new Date(), 'YYYY-MM-DD')
const price = formatCurrency(12345.67)
const phone = formatPhone('13888888888')
```

## 主题配置

主题配置在 `src/theme/theme.ts`，包含：

- 色彩系统
- 字体系统
- 间距系统
- 圆角系统
- 阴影系统
- 断点系统
- 动画配置

使用 Tailwind CSS 类名或直接导入主题配置：

```typescript
import theme from '@/theme/theme'

const primaryColor = theme.colors.primary[600]
```

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 注意事项

1. 所有 API 请求必须使用环境变量配置的 `VITE_API_BASE_URL`
2. TypeScript 严格模式已启用，请确保类型正确
3. 组件需要遵循 React Hooks 规范
4. 代码提交前请运行 `npm run lint` 和 `npm run type-check`

## 后续开发

当前版本只包含基础框架，具体页面功能将在后续任务中实现：

- [ ] 用户登录注册页面
- [ ] 信息收集表单
- [ ] 方案展示和对比
- [ ] 方案详情页
- [ ] 景点美食浏览
- [ ] 订单确认和支付

## 许可证

ISC

## 联系方式

如有问题，请联系开发团队。
