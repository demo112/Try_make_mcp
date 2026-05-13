import sys
import os
import json
import subprocess
import threading
import time

def read_stream(stream, output_list):
    """读取流并存入列表"""
    for line in stream:
        output_list.append(line.decode('utf-8').strip())

def verify_mcp_exe(exe_path):
    """
    验证 MCP EXE 是否能正常启动并响应 JSON-RPC 请求
    """
    print(f"🔍 Verifying MCP EXE: {exe_path}")
    
    if not os.path.exists(exe_path):
        print(f"❌ Error: EXE not found at {exe_path}")
        return False

    # 启动进程
    process = subprocess.Popen(
        [exe_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0  # 无缓冲
    )

    stderr_lines = []
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, stderr_lines))
    stderr_thread.daemon = True
    stderr_thread.start()

    try:
        # 1. 发送 initialize 请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "MCPVerifier",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending 'initialize' request...")
        process.stdin.write((json.dumps(init_request) + "\n").encode('utf-8'))
        process.stdin.flush()

        # 读取响应 (设置超时)
        start_time = time.time()
        response_line = None
        while time.time() - start_time < 10:  # 10秒超时
            line = process.stdout.readline()
            if line:
                response_line = line.decode('utf-8').strip()
                break
            time.sleep(0.1)

        if not response_line:
            print("❌ Timeout waiting for 'initialize' response")
            print("📝 Stderr output:")
            for line in stderr_lines:
                print(line)
            return False

        print(f"📥 Received: {response_line[:100]}...")
        response = json.loads(response_line)

        if "result" not in response:
            print(f"❌ Invalid response: {response}")
            return False

        server_info = response["result"].get("serverInfo", {})
        print(f"✅ Server initialized: {server_info.get('name')} v{server_info.get('version')}")

        # 2. 发送 initialized 通知
        init_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write((json.dumps(init_notif) + "\n").encode('utf-8'))
        process.stdin.flush()

        # 3. 请求 tools/list
        list_tools_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        print("📤 Sending 'tools/list' request...")
        process.stdin.write((json.dumps(list_tools_req) + "\n").encode('utf-8'))
        process.stdin.flush()

        # 读取响应
        response_line = process.stdout.readline().decode('utf-8').strip()
        print(f"📥 Received: {response_line[:100]}...")
        response = json.loads(response_line)
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool.get('description', '')[:50]}...")
            return True
        else:
            print(f"❌ Failed to list tools: {response}")
            return False

    except Exception as e:
        print(f"❌ Exception during verification: {e}")
        return False
    finally:
        # 清理进程
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        
        if stderr_lines:
            print("📝 Stderr output (during execution):")
            for line in stderr_lines:
                print(line)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_mcp.py <path_to_exe>")
        sys.exit(1)
    
    exe_path = sys.argv[1]
    success = verify_mcp_exe(exe_path)
    sys.exit(0 if success else 1)
