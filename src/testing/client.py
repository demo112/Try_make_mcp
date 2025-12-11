import json
import subprocess
import threading
import time
import os
from typing import List, Dict, Any, Optional

class McpTestClient:
    """
    一个简单的 MCP 客户端，用于测试。
    支持启动 MCP Server 子进程，并通过 Stdio 发送 JSON-RPC 请求。
    """

    def __init__(self, command: List[str], env: Dict[str, str] = None):
        self.command = command
        self.env = env or os.environ.copy()
        self.process: Optional[subprocess.Popen] = None
        self.stderr_lines: List[str] = []
        self._seq_id = 0
        self._lock = threading.Lock()

    def start(self):
        """启动 MCP Server 子进程"""
        print(f"🚀 Starting MCP Client with command: {self.command}")
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
            bufsize=0  # Unbuffered
        )
        
        # 启动 stderr 读取线程
        self.stderr_lines = []
        t = threading.Thread(target=self._read_stderr)
        t.daemon = True
        t.start()

    def stop(self):
        """停止 MCP Server 子进程"""
        if self.process:
            print("🛑 Stopping MCP Client...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def _read_stderr(self):
        """后台线程读取 stderr"""
        if not self.process:
            return
        for line in self.process.stderr:
            decoded = line.decode('utf-8', errors='replace').strip()
            self.stderr_lines.append(decoded)
            # print(f"[STDERR] {decoded}") # Optional: Debug output

    def send_request(self, method: str, params: Dict = None, timeout: float = 5.0) -> Dict:
        """发送请求并等待响应"""
        if not self.process:
            raise RuntimeError("Process not started. Call start() first.")

        with self._lock:
            self._seq_id += 1
            request_id = self._seq_id

        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        # Send
        json_str = json.dumps(payload)
        self.process.stdin.write((json_str + "\n").encode('utf-8'))
        self.process.stdin.flush()

        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            line = self.process.stdout.readline()
            if not line:
                if self.process.poll() is not None:
                    raise RuntimeError(f"Process exited unexpectedly with code {self.process.returncode}. Stderr: {self.stderr_lines}")
                time.sleep(0.1)
                continue
            
            try:
                response = json.loads(line.decode('utf-8'))
                # 只处理这是我们请求的响应
                if response.get("id") == request_id:
                    if "error" in response:
                        raise RuntimeError(f"MCP Error: {response['error']}")
                    return response.get("result")
            except json.JSONDecodeError:
                continue # Skip non-json lines

        raise TimeoutError(f"Request {method} timed out after {timeout}s")

    def send_notification(self, method: str, params: Dict = None):
        """发送通知 (不等待响应)"""
        if not self.process:
            raise RuntimeError("Process not started")
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        json_str = json.dumps(payload)
        self.process.stdin.write((json_str + "\n").encode('utf-8'))
        self.process.stdin.flush()

    def initialize(self):
        """执行标准的初始化流程"""
        # 1. initialize
        init_result = self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "McpTestClient", "version": "1.0"}
        })
        
        # 2. initialized notification
        self.send_notification("notifications/initialized")
        return init_result

    def list_tools(self) -> List[Dict]:
        """获取工具列表"""
        result = self.send_request("tools/list")
        return result.get("tools", [])

    def call_tool(self, name: str, arguments: Dict = None) -> Any:
        """调用工具"""
        result = self.send_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
        return result.get("content", [])

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
