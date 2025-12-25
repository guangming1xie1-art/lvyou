# 旅游智能助手 MVP UI 设计规范

## 1. 核心设计理念
- **风格**：欧美现代极简主义 (Western Modern Minimalist)
- **重点**：内容为王，强调高质量旅游和美食图片。
- **元素**：大圆角 (24px+), 柔和阴影, 渐变色, 充足的留白。

## 2. 色彩规范 (Color Palette)

### 主色 (Primary) - 深蓝
用于品牌识别、主导航、主要操作按钮。
- `Primary 600`: `#2563eb` (Brand Color)
- `Primary 900`: `#1e3a8a` (Deep Blue for Headers/Hero)

### 辅色 (Secondary) - 暖橙
用于强调色、行动召唤按钮 (CTA)、价格显示、高亮状态。
- `Secondary 500`: `#f97316`
- `Secondary 600`: `#ea580c`

### 中性色 (Neutral)
- `Background`: `#f9fafb` (Gray 50)
- `Surface`: `#ffffff` (White)
- `Text Main`: `#111827` (Gray 900)
- `Text Body`: `#4b5563` (Gray 600)
- `Text Muted`: `#9ca3af` (Gray 400)

## 3. 字体规范 (Typography)

### 字体族
- `Sans-serif`: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- 强调现代感与易读性。

### 字号与权重
- `Hero Heading`: 72px / Bold (Mobile: 36px)
- `Page Title`: 48px / Bold
- `Section Title`: 30px / Bold
- `Card Title`: 20px / Bold
- `Body Text`: 16px / Regular
- `Caption`: 14px / Medium

## 4. 交互说明 (Interaction Design)

### 状态变化
- **Hover**: 阴影加深，图片轻微放大 (Scale 1.05)，按钮颜色深浅变化。
- **Active**: 点击时按钮轻微收缩 (Scale 0.95)。
- **Loading**: 使用骨架屏 (Skeleton Screens) 代替传统的转圈加载。

### 页面过渡
- 推荐使用平滑的淡入淡出 (Fade In) 或上下滑动动画。

## 5. 响应式设计 (Responsive Design)

- **Mobile (< 640px)**: 容器全宽，堆叠布局，字号缩小。
- **Tablet (640px - 1024px)**: 2列网格布局。
- **Desktop (> 1024px)**: 3-4列网格，最大容器宽度 1280px。

## 6. React Native 适配方案

- **布局**: 使用 Flexbox (Yoga 引擎) 实现响应式。
- **组件映射**:
  - `div` -> `View`
  - `span/p/h1` -> `Text`
  - `img` -> `Image`
  - `Link` -> `Pressable` / `TouchableOpacity`
- **样式**: 将 Tailwind 转化为 `StyleSheet` 对象，推荐使用 `nativewind` 库以复用 Tailwind 类名。
- **图片**: 在移动端需注意图片长宽比适配，推荐使用 `FastImage` 提升瀑布流性能。

---
*本规范旨在为前端开发提供清晰的视觉指导，确保 MVP 版本的高质量交付。*
