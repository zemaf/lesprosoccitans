# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['/Users/imaf/my_python_projects/pro_occitans/src/main/python/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=['/Users/imaf/fbs_ps6_venv/lib/python3.9/site-packages/fbs/freeze/hooks'],
    hooksconfig={},
    runtime_hooks=['/Users/imaf/my_python_projects/pro_occitans/target/PyInstaller/fbs_pyinstaller_hook.py'],
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
    [],
    exclude_binaries=True,
    name='Les_Pros_Occitans',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/Users/imaf/my_python_projects/pro_occitans/target/Icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Les_Pros_Occitans',
)
app = BUNDLE(
    coll,
    name='Les_Pros_Occitans.app',
    icon='/Users/imaf/my_python_projects/pro_occitans/target/Icon.icns',
    bundle_identifier=None,
)
