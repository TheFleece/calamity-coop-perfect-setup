# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['terraria_installer.py'],
    pathex=[],
    binaries=[],
    # ИЗМЕНЕНИЕ ЗДЕСЬ: Убраны json и zip, оставлены только ресурсы интерфейса
    datas=[('icon.ico', '.'), ('banner.jpg', '.')],
    hiddenimports=['PIL._tkinter_finder'],
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
    name='Calamity_Ultra_Installer',  # Можно сразу дать красивое имя
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Отключает черное окно консоли
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)