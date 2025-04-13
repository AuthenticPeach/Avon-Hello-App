# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.__main__

a = Analysis(
    ['avon-hello.py'],
    pathex=[],
    binaries=[],
    datas=[('delete_icon.png', '.'), ('Avon256.ico', '.'), ('settings.conf', '.'), ('avon_hello.db', '.')],
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
    [],
    exclude_binaries=True,
    name='avon-hello',
    debug=False,
    bootloader_ignore_signals=False,
    icon='Avon256.ico',
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='avon-hello',
)
