# 深度思考预览功能测试指南

## 测试环境准备

### 1. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

## 配置测试渠道

### 方式一：使用 OpenAI o1 模型

1. 访问管理员后台：http://localhost:8000/admin
2. 登录管理员账号
3. 进入"渠道管理"
4. 添加新渠道：
   - 渠道名称：OpenAI o1
   - Base URL：https://api.openai.com/v1
   - API Key：你的 OpenAI API Key
   - Model ID：o1-preview 或 o1-mini
   - RPM 限制：根据你的配额设置
   - 开启状态：启用

### 方式二：使用兼容 OpenAI 格式的其他服务

如果你使用的是其他支持 reasoning 的 API 服务（如 Azure OpenAI、第三方代理等），配置方式类似：

1. Base URL：你的 API 服务地址
2. API Key：你的 API Key
3. Model ID：支持 reasoning 的模型 ID

## 测试步骤

### 测试 1：基本功能测试

1. 访问用户聊天页面：http://localhost:8000/
2. 在模型选择器中选择支持 reasoning 的模型（如 o1-preview）
3. 发送一个需要深度思考的问题，例如：
   ```
   请解释量子纠缠的原理，并说明它在量子计算中的应用
   ```
4. 观察：
   - 消息发送后，应该看到流式输出
   - 在 AI 回复下方应该出现"思考过程"折叠面板
   - 点击"思考过程"可以展开查看详细的推理过程

### 测试 2：流式更新测试

1. 发送一个复杂问题
2. 观察思考过程是否实时更新
3. 观察最终回复是否正常显示
4. 验证思考过程和回复内容是否分开显示

### 测试 3：折叠/展开功能测试

1. 发送消息并等待回复完成
2. 点击"思考过程"按钮展开
3. 验证思考内容是否完整显示
4. 再次点击按钮折叠
5. 验证折叠后显示字符数统计

### 测试 4：兼容性测试

1. 切换到不支持 reasoning 的模型（如 gpt-3.5-turbo）
2. 发送消息
3. 验证：
   - 消息正常发送和接收
   - 不显示"思考过程"面板
   - 其他功能正常工作

### 测试 5：多轮对话测试

1. 使用支持 reasoning 的模型
2. 进行多轮对话
3. 验证每条 AI 回复都能正确显示思考过程
4. 验证历史消息的思考过程可以正常展开/折叠

## 预期结果

### 正常情况

- ✅ 思考过程实时流式显示
- ✅ 思考内容和回复内容分开显示
- ✅ 折叠/展开功能正常
- ✅ 显示字符数统计
- ✅ 样式美观，与整体 UI 一致

### 边界情况

- ✅ 不支持 reasoning 的模型不显示思考面板
- ✅ 空的 reasoning 内容不显示面板
- ✅ 网络错误时正常显示错误信息

## 调试技巧

### 查看浏览器控制台

打开浏览器开发者工具（F12），查看：

1. **Network 标签**：
   - 查看 `/api/chat/completions` 请求
   - 检查 SSE 流式响应
   - 验证响应中是否包含 `reasoning_content` 字段

2. **Console 标签**：
   - 查看是否有 JavaScript 错误
   - 查看 `console.log` 输出的调试信息

### 检查 API 响应格式

正常的流式响应应该包含：

```
data: {"choices":[{"delta":{"reasoning_content":"思考内容..."}}]}

data: {"choices":[{"delta":{"content":"回复内容..."}}]}

data: [DONE]
```

### 常见问题排查

1. **思考面板不显示**：
   - 检查模型是否支持 reasoning
   - 查看浏览器控制台是否有错误
   - 检查 API 响应是否包含 `reasoning_content`

2. **内容显示不完整**：
   - 检查网络连接
   - 查看是否有 JavaScript 错误
   - 验证流式处理逻辑

3. **样式显示异常**：
   - 清除浏览器缓存
   - 检查 Tailwind CSS 是否正确加载
   - 验证组件导入是否正确

## 模拟测试数据

如果没有真实的 o1 API，可以修改后端代码模拟返回 reasoning 内容进行测试：

```python
# 在 backend/app/services/chat.py 中添加模拟数据
# 仅用于测试，生产环境请删除

# 在流式响应中添加模拟的 reasoning_content
yield f'data: {json.dumps({"choices":[{"delta":{"reasoning_content":"这是模拟的思考过程..."}}]})}\n\n'
yield f'data: {json.dumps({"choices":[{"delta":{"content":"这是模拟的回复内容..."}}]})}\n\n'
```

## 性能测试

1. 发送长文本问题，观察性能
2. 快速连续发送多条消息
3. 检查内存使用情况
4. 验证流式更新的流畅度

## 用户体验测试

1. 在不同屏幕尺寸下测试（桌面、平板、手机）
2. 测试深色/浅色主题（如果支持）
3. 测试键盘导航和无障碍功能
4. 收集用户反馈

## 总结

完成以上测试后，深度思考预览功能应该能够：

- 正确显示支持 reasoning 的模型的思考过程
- 提供良好的用户体验
- 与现有功能完美兼容
- 性能稳定可靠
