#!/usr/bin/env python3
import os
import subprocess
import time
import signal

# 设置环境变量
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 启动API服务
print("Starting mPower_Rag API server...")
process = subprocess.Popen(
    ['python3', '-m', 'uvicorn', 'src.api.main:app', '--host', '0.0.0.0', '--port', '8000'],
    cwd='/home/qw/.openclaw/workspace/projects/mpower_Rag',
    env=os.environ,
    stdout=open('/tmp/mpower_api_stdout.log', 'w'),
    stderr=open('/tmp/mpower_api_stderr.log', 'w')
)

print(f"API server started with PID: {process.pid}")

# 保持进程运行
try:
    while True:
        time.sleep(60)
        if process.poll() is not None:
            print(f"Process exited with code: {process.poll()}")
            break
except KeyboardInterrupt:
    print("Shutting down...")
    process.terminate()
