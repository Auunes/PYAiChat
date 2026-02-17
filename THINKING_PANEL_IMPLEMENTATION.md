# 深度思考预览功能实现说明

## 功能概述

已成功实现类似 CherryStudio 的深度思考预览框功能，用于显示支持 reasoning 的模型（如 OpenAI o1）的思考过程。

## 实现细节

### 1. 类型定义更新 (`frontend/src/types/index.ts`)

在 `ChatMessage` 接口中添加了 `reasoning` 字段：

```typescript
export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
  reasoning?: string  // 思考过程（仅 reasoning 模型）
}
```

### 2. 聊天状态管理更新 (`frontend/src/stores/chat.ts`)

修改了 `sendMessage` 函数，支持处理流式响应中的 `reasoning_content`：

- 初始化消息时包含空的 `reasoning` 字段
- 在流式处理中分别处理 `delta.reasoning_content` 和 `delta.content`
- `reasoning_content` 用于显示模型的思考过程
- `content` 用于显示最终回复

### 3. ThinkingPanel 组件 (`frontend/src/components/ThinkingPanel.vue`)

创建了专门的思考预览组件，特性包括：

- **可折叠设计**：默认折叠，点击展开查看详细思考过程
- **字符计数**：折叠时显示思考内容的字符数
- **样式优化**：使用灰色背景和等宽字体，便于阅读思考过程
- **动画效果**：展开/折叠时有平滑的过渡动画
- **条件渲染**：只在有 reasoning 内容时显示

### 4. 聊天页面集成 (`frontend/src/views/Chat.vue`)

在聊天消息显示中集成了 ThinkingPanel 组件：

- 导入 ThinkingPanel 组件
- 在 assistant 消息下方显示思考面板
- 传递 `message.reasoning` 作为 props

## 工作原理

### OpenAI API 流式响应格式

支持 reasoning 的模型（如 o1）在流式响应中会返回两种内容：

```json
{
  "choices": [{
    "delta": {
      "reasoning_content": "思考过程的文本...",
      "content": "最终回复的文本..."
    }
  }]
}
```

### 数据流处理

1. **后端**：直接转发上游 API 的流式响应，保持原始格式
2. **前端 API 层**：解析 SSE 流，提取 JSON 数据
3. **状态管理层**：分别累积 `reasoning_content` 和 `content`
4. **UI 层**：实时显示内容，思考过程可折叠查看

## 使用方法

### 配置支持 reasoning 的模型

在管理员后台添加支持 reasoning 的渠道，例如：

- **渠道名称**：OpenAI o1
- **Base URL**：https://api.openai.com/v1
- **API Key**：你的 OpenAI API Key
- **Model ID**：o1-preview 或 o1-mini

### 用户体验

1. 用户在聊天页面选择支持 reasoning 的模型
2. 发送消息后，AI 开始思考
3. 思考过程实时流式显示在折叠面板中
4. 最终回复显示在主消息区域
5. 用户可以点击"思考过程"查看详细的推理过程

## 兼容性

- **向后兼容**：不支持 reasoning 的模型不会显示思考面板
- **渐进增强**：reasoning 字段为可选，不影响现有功能
- **自动检测**：根据 API 响应自动判断是否显示思考面板

## 技术特点

1. **实时流式显示**：思考过程和回复内容同步流式更新
2. **性能优化**：使用 Vue 3 响应式系统，高效更新 UI
3. **用户友好**：可折叠设计，不影响正常对话体验
4. **样式统一**：与整体 UI 风格保持一致

## 测试建议

1. 使用支持 reasoning 的模型（如 OpenAI o1）测试
2. 发送复杂问题，观察思考过程的显示
3. 测试折叠/展开功能
4. 验证与普通模型的兼容性

## 注意事项

- 思考过程可能很长，建议使用滚动查看
- 某些模型可能不返回 reasoning_content，这是正常的
- 思考过程使用等宽字体，便于阅读代码和结构化内容
