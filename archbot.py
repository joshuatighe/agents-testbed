import argparse
import sys

parser = argparse.ArgumentParser(description="run the archbot coding agent on a repository.")
parser.add_argument("--target", default="./", help="repository the agent works in (default: current directory)")
parser.add_argument("--max-steps", type=int, default=15, help="maximum agent loop iterations (default: 15)")
parser.add_argument("--log-file", help="write all logs to this file")
args = parser.parse_args()

if args.log_file:
    class Tee:
        def __init__(self, *streams):
            self.streams = streams

        def write(self, data):
            for s in self.streams:
                s.write(data)
                s.flush()

        def flush(self):
            for s in self.streams:
                s.flush()

# Step 1: Give the Agent Tools
from pathlib import Path

ROOT = Path(args.target).resolve()

if not ROOT.is_dir():
    sys.exit(f"Target is not a directory: {ROOT}")

if args.log_file:
    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    sys.stdout = Tee(sys.__stdout__, open(log_path, "w"))

def list_files():
    return [
        str(p.relative_to(ROOT))
        for p in ROOT.rglob("*")
        if p.is_file()
    ]

def read_file(path):
    target = (ROOT / path).resolve()

    if not target.is_relative_to(ROOT):
        raise ValueError("Access outside workspace is not allowed")

    return target.read_text()

def write_file(path, content):
    target = (ROOT / path).resolve()

    if not target.is_relative_to(ROOT):
        raise ValueError("Access outside workspace is not allowed")

    # LLMs sometimes pass literal '\n' escape sequences instead of real newlines
    content = content.replace("\\n", "\n").replace("\\t", "\t")
    target.write_text(content)
    return f"Updated {path}"


# step 2: let the agent execute code
import subprocess

def run_python(path):
    target = (ROOT / path).resolve()

    if not target.is_relative_to(ROOT):
        raise ValueError("Access outside workspace is not allowed")

    try:
        result = subprocess.run(
            ["python", str(target)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )

        return {
            "return_code": result.returncode,
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-4000:]
        }

    except subprocess.TimeoutExpired:
        return {
            "return_code": -1,
            "stdout": "",
            "stderr": "Execution timed out."
        }

# step 3: build the agent loop
from ollama import chat

tools = [
    list_files,
    read_file,
    write_file,
    run_python
]

messages = [
    { # system's instructions/restrictions to the agent
        "role": "system",
        "content": """
You are a coding agent named archbot.

Work only inside the provided workspace.
Only inspect files and do not modify them, unless the file is arch.md, in which case you can modify.
"""
    },
    { # user's unstructions to the agent
        "role": "user",
        "content": """
You are to review this codebase and update (create if does not exist) an arch.md document.
You are the sole owner of this file, and are responsible for keeping it nicely formatted and up to date detailing the codebases architecture. 
You are to assume other agents will be working on the codebase and will rely on this file
"""
    }
] # end of messages

available = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_python": run_python
}

# this is my agent loop
loop_count = 0

while loop_count < args.max_steps:
    # printing current working step and status
    loop_count += 1
    print(f"\n--- Loop iteration {loop_count} ---")
    print("[Harness] Sending messages to model...")

    response = chat( # ollama method
        model="qwen3",
        messages=messages,
        tools=tools
    )

    messages.append(response.message)

    if not response.message.tool_calls:
        print(f"[Harness] No tool calls — agent finished after {loop_count} iteration(s).")
        print(response.message.content)
        break

    print(f"[Harness] Model requested {len(response.message.tool_calls)} tool call(s):")
    for call in response.message.tool_calls:
        function = call.function.name
        arguments = call.function.arguments
        print(f"  [Tool] {function}({arguments})")

        if function in available:
            result = available[function](**arguments)
        else:
            result = "Unknown tool"

        print(f"  [Result] {str(result)[:200]}")
        messages.append({
            "role": "tool",
            "tool_name": function,
            "content": str(result)
        })
else:
    print(f"\n[Harness] Stopped: reached --max-steps limit ({args.max_steps}).")