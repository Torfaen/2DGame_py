import os
import sys


def _base_path():
    """
    返回运行时资源根目录：
    - 源码环境：项目根目录（src 的上一级）
    - 打包环境（PyInstaller）：sys._MEIPASS
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    # __file__ 位于 src/ 中
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def resource_path(*parts):
    """
    将传入的路径片段拼接到资源根目录下。
    示例：resource_path('assets', 'sprites', 'player')
    """
    return os.path.join(_base_path(), *parts)


def resolve_relative_path(relative_path):
    """
    兼容原始配置中的 '../assets/...' 写法。
    无论在源码还是打包环境，都会指向资源根目录下的实际文件。
    """
    normalized = relative_path.replace("\\", "/")
    while normalized.startswith("../"):
        normalized = normalized[3:]
    normalized = normalized.lstrip("./")
    normalized = normalized.replace("/", os.sep)
    return os.path.join(_base_path(), normalized)

