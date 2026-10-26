import os
from agent_framework import tool

@tool(approval_mode="never_require")
def list_files(directory: str):
    """列出指定目录下的所有文件。"""
    print(f"[DEBUG] list_files 被调用，目录：{directory}")
    if not os.path.isdir(directory):
        return [f"目录不存在：{directory}"]
    result = os.listdir(directory)
    print(f"[DEBUG] list_files 结果：{result}")
    return result

@tool(approval_mode="always_require")
def read_file(file_path: str):
    """读取指定文件的内容。"""
    print(f"[DEBUG] read_file 被调用，文件路径：{file_path}")
    if not os.path.isfile(file_path):
        return f"文件不存在：{file_path}"
    with open(file_path, "r", encoding="utf-8") as f:
        result = f.read()
        # print(f"[DEBUG] read_file 结果：{result}")
        return result