from typing import Any, List, Optional
import json
import os
import requests
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials

# Initialize FastMCP server
mcp = FastMCP(
    "kb",
    title="Knowledge Base API",
    description="A server that provides access to the Volcengine knowledge base API"
)

# Constants
CONFIG_DIR = os.path.expanduser("~/.config/volc_kb_mcp")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_DOMAIN = "api-knowledgebase.mlp.cn-beijing.volces.com"

def load_config() -> dict:
    """Load configuration from config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config: dict):
    """Save configuration to config file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@mcp.tool()
async def configure(access_key: str, secret_key: str, account_id: int, collection_name: str) -> str:
    """Configure the MCP server with your Volcengine credentials.
    
    Args:
        access_key: Your Volcengine access key
        secret_key: Your Volcengine secret key
        account_id: Your Volcengine account ID
        collection_name: The name of your knowledge base collection
    Returns:
        str: Configuration status message
    """
    config = {
        "access_key": access_key,
        "secret_key": secret_key,
        "account_id": account_id,
        "collection_name": collection_name,
        "domain": DEFAULT_DOMAIN,
        "project_name": "default"
    }
    
    try:
        # Test the credentials
        credentials = Credentials(access_key, secret_key, "air", "cn-north-1")
        r = Request()
        r.set_method("GET")
        r.set_host(DEFAULT_DOMAIN)
        r.set_path("/")
        r.set_headers({"V-Account-Id": str(account_id)})
        SignerV4.sign(r, credentials)
        
        # If no exception, save the config
        save_config(config)
        return json.dumps({"status": "success", "message": "Configuration saved successfully"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to validate credentials: {str(e)}"})

def get_credentials():
    """Get credentials from config file."""
    config = load_config()
    if not config:
        raise ValueError(
            "Credentials not configured. Please use the configure() tool first with your Volcengine credentials."
        )
    return config

def prepare_request(method: str, path: str, params: Optional[dict] = None, data: Optional[dict] = None, doseq: int = 0) -> Request:
    """Prepare a request with proper headers and authentication."""
    config = get_credentials()
    
    if params:
        for key in params:
            if isinstance(params[key], (int, float, bool)):
                params[key] = str(params[key])
            elif isinstance(params[key], list) and not doseq:
                params[key] = ",".join(params[key])
    
    r = Request()
    r.set_shema("http")
    r.set_method(method)
    r.set_connection_timeout(10)
    r.set_socket_timeout(10)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Host": config["domain"],
        "V-Account-Id": str(config["account_id"]),
    }
    r.set_headers(headers)
    if params:
        r.set_query(params)
    r.set_host(config["domain"])
    r.set_path(path)
    if data is not None:
        r.set_body(json.dumps(data))

    credentials = Credentials(config["access_key"], config["secret_key"], "air", "cn-north-1")
    SignerV4.sign(r, credentials)
    return r

@mcp.tool()
async def search_knowledge(query: str) -> str:
    """Search the knowledge base for relevant information.
    
    Args:
        query: The search query string
    Returns:
        str: The search results in JSON format
    """
    config = get_credentials()
    method = "POST"
    path = "/api/knowledge/collection/search_knowledge"
    request_params = {
        "project": config["project_name"],
        "name": config["collection_name"],
        "query": query,
        "limit": 28,
        "pre_processing": {
            "need_instruction": True,
            "return_token_usage": True,
            "messages": [
                {"role": "system", "content": ""},
                {"role": "user", "content": query}
            ],
            "rewrite": True
        },
        "dense_weight": 0.5,
        "post_processing": {
            "get_attachment_link": True,
            "rerank_only_chunk": False,
            "rerank_switch": True,
            "chunk_group": True,
            "rerank_model": "base-multilingual-rerank",
            "retrieve_count": 40,
            "chunk_diffusion_count": 0
        }
    }

    try:
        info_req = prepare_request(method=method, path=path, data=request_params)
        rsp = requests.request(
            method=info_req.method,
            url=f"http://{config['domain']}{info_req.path}",
            headers=info_req.headers,
            data=info_req.body,
            timeout=30
        )
        rsp.raise_for_status()
        return rsp.text
    except Exception as e:
        return json.dumps({"error": f"Error in search_knowledge: {str(e)}"})

@mcp.tool()
async def chat_completion(messages: List[dict], stream: bool = False, temperature: float = 0.7) -> str:
    """Get a chat completion response from the model.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        stream: Whether to stream the response
        temperature: Temperature parameter for response generation
    Returns:
        str: The chat completion response in JSON format
    """
    config = get_credentials()
    method = "POST"
    path = "/api/knowledge/chat/completions"
    request_params = {
        "messages": messages,
        "stream": stream,
        "return_token_usage": True,
        "model": "Deepseek-r1",
        "max_tokens": 4096,
        "temperature": temperature,
        "model_version": "250120"
    }

    try:
        info_req = prepare_request(method=method, path=path, data=request_params)
        rsp = requests.request(
            method=info_req.method,
            url=f"http://{config['domain']}{info_req.path}",
            headers=info_req.headers,
            data=info_req.body,
            timeout=30
        )
        rsp.raise_for_status()
        return rsp.text
    except Exception as e:
        return json.dumps({"error": f"Error in chat_completion: {str(e)}"})

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 