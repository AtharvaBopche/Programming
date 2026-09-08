# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for C Programming Recovery Tracker Desktop App

import os

block_cipher = None

a = Analysis(
    ['app_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('public', 'public'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms',
        'webview.platforms.edgechromium',
        'clr_loader',
        'clr_loader.ffi',
        'clr_loader.util',
        'clr_loader.util.runtime_spec',
        'pythonnet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='C_Recovery_Tracker_App',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
