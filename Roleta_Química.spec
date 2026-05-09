# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.building.datastruct import Tree

a = Analysis(
    ['telas_e_botoes.py'],
    pathex=['.'],
    binaries=[],
    datas=[],  
    hiddenimports=[
        'win32timezone',
        'roda_animada',
        'introducao',
        'predefinicoes',
        'kivy.core.audio.audio_gstplayer',
        'kivy.core.video.video_gstplayer',
        'kivy.lib.gstplayer._gstplayer',
        'kivy_deps.gstreamer',    
        'loading_screen',
        'creditos',
        'numpy._core._exceptions',
        'historico',
    ],
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
    name='Roleta_Quimica',      
    debug=False,                 #True enquanto depura
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,               #True enquanto depura
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icone.ico',           
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    # >>> Coloque as PASTAS AQUI (recursivo):
    Tree('assets',  prefix='assets'),
    Tree('configs', prefix='configs'),
    Tree('sons',    prefix='sons'),
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Roleta_Quimica',
)
