# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('.env', '.')],  # Include .env file in the bundle
    hiddenimports=[
        'fastapi', 
        'uvicorn', 
        'langchain', 
        'langchain_community',
        'langchain_ollama',
        'config',
        'vision_analyzer',
        'llm_task_analyzer',
        'tasks',
        'listener',
        'agent'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Collect additional data files if needed
extra_data = collect_data_files('langchain_community')
a.datas.extend(extra_data)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='intervene',
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