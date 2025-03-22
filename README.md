# Volcengine Knowledge Base MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

Claude Desktop 的火山引擎知识库 MCP 服务器，提供知识库搜索和对话功能。

## 特性

- 🔍 知识库搜索
- 💬 对话补全
- 🔐 安全的凭证管理
- 🚀 简单易用的配置

## 快速开始

### 前提条件

- Python 3.10 或更高版本
- Claude Desktop
- 你需要注册一个火山引擎账号，开通知识库服务，并且创建一个知识库

### 安装

1. 克隆仓库：
```bash
git clone git@github.com:suqidan/volc-kb-mcp.git
cd volc-kb-mcp
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

### 配置 Claude Desktop

编辑 Claude Desktop 配置文件：

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置：

```json
{
    "mcpServers": {
        "kb": {
            "command": "python",
            "args": [
                "/path/to/kb_mcp.py"
            ]
        }
    }
}
```

### 使用方法
设置好 Claude MCP JSON 配置后，你只需要直接告诉 Claude 你要使用知识库，它就会询问你添加对应的信息，包含 ak, sk, account_id 以及 collection_namme
![Uploading image.png…]()

1. 首次使用时配置凭证：
```python
await configure(
    access_key="your_access_key",
    secret_key="your_secret_key",
    account_id=your_account_id,
    collection_name="your_collection_name"
)
```

2. 搜索知识库：
```python
result = await search_knowledge("你的查询")
```

3. 对话补全：
```python
messages = [
    {"role": "system", "content": "你是一个有帮助的助手"},
    {"role": "user", "content": "你好"}
]
response = await chat_completion(messages)
```

## API 文档

### configure
配置火山引擎凭证和知识库设置。

**参数：**
- `access_key` (str): 火山引擎访问密钥
- `secret_key` (str): 火山引擎安全密钥
- `account_id` (int): 火山引擎账户ID
- `collection_name` (str): 知识库集合名称

### search_knowledge
搜索知识库。

**参数：**
- `query` (str): 搜索查询字符串

### chat_completion
获取对话补全响应。

**参数：**
- `messages` (List[dict]): 对话消息列表
- `stream` (bool, 可选): 是否使用流式响应
- `temperature` (float, 可选): 温度参数

## 安全性

- 所有凭证都安全存储在用户本地
- 配置文件权限仅限当前用户访问
- 不会将凭证发送到火山引擎 API 之外的任何地方

## 故障排除

如果遇到问题：

1. 确认凭证信息正确
2. 检查配置文件权限
3. 查看 Claude Desktop 日志文件
4. 如果需要重新配置，删除 `~/.config/volc_kb_mcp/config.json`

## 贡献

欢迎提交 Pull Requests！对于重大更改，请先开 issue 讨论您想要更改的内容。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 作者

suqidan

## 致谢

- [火山引擎](https://www.volcengine.com/)
- [Claude Desktop](https://claude.ai/)
- [Model Context Protocol](https://modelcontextprotocol.io/) 
