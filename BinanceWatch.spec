# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['binancewatch.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['rumps', 'requests', 'urllib3', 'certifi'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'PIL', 'scipy'],
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
    name='BinanceWatch',
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
)

app = BUNDLE(
    exe,
    name='BinanceWatch.app',
    icon='icon.icns',
    bundle_identifier='com.binancewatch.app',
    info_plist={
        'LSUIElement': True,
        'CFBundleName': 'BinanceWatch',
        'CFBundleDisplayName': 'BinanceWatch',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
)
