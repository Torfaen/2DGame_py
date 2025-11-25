# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import inspect

spec_path = Path(inspect.getfile(inspect.currentframe())).resolve()
project_root = spec_path.parent.parent

data_dirs = [
    "assets",
    "config",
    "docs",
    "excel",
    "map",
    "paopaotang",
    "tools",
]

data_files = [
    "run.bat",
    "test_chain_logic.md",
    "代码答案集.md",
    "代码详解.md",
    "代码问题集.md",
    "快速参考.md",
    "项目入门指南.md",
]

project_datas = []

for folder in data_dirs:
    folder_path = project_root / folder
    if folder_path.exists():
        project_datas.append((str(folder_path), folder))

for single_file in data_files:
    file_path = project_root / single_file
    if file_path.exists():
        project_datas.append((str(file_path), single_file))


a = Analysis(
    ['main2.py'],
    pathex=[],
    binaries=[],
    datas=project_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
