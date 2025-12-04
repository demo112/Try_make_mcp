# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['mcp.server.fastmcp', 'src.common', 'src.apps.md_converter.converters', 'uvicorn', 'starlette', 'sse_starlette', 'pydantic', 'anyio', 'html5lib', 'openpyxl', 'docx', 'markdown', 'bs4']
tmp_ret = collect_all('xhtml2pdf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('reportlab')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\Administrator\\Documents\\trae_projects\\Try_make_mcp\\src\\apps\\md_converter\\server.py'],
    pathex=['C:\\Users\\Administrator\\Documents\\trae_projects\\Try_make_mcp'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='md_converter',
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
