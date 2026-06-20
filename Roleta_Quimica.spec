# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
from kivy_deps import sdl2, glew, angle
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, hookspath, runtime_hooks

# Usa o hook alternativo do Kivy e inclui só os providers desejados.
# Nada de gstplayer/gstreamer aqui.
kivy_deps = get_deps_minimal(
    window='sdl2',
    text='sdl2',
    image=['sdl2', 'pil'],
    audio='ffpyplayer',
    video='ffpyplayer',
    clipboard=True,
    camera=None,
    spelling=None,
)

# Coleta arquivos e DLLs do ffpyplayer, se estiver instalado no Python 3.12.
ffpyplayer_datas = collect_data_files('ffpyplayer')
ffpyplayer_binaries = collect_dynamic_libs('ffpyplayer')

manual_hiddenimports = [
    'win32timezone',

    # arquivos do projeto
    'roda_animada',
    'introducao',
    'predefinicoes',
    'loading_screen',
    'creditos',
    'historico',

    # numpy
    'numpy._core._exceptions',

    # Kivy essenciais que às vezes entram via import dinâmico
    'kivy',
    'kivy.config',
    'kivy.app',
    'kivy.clock',
    'kivy.factory',
    'kivy.lang',
    'kivy.properties',
    'kivy.metrics',
    'kivy.resources',

    # Providers desejados
    'kivy.core.window.window_sdl2',
    'kivy.core.text.text_sdl2',
    'kivy.core.image.img_sdl2',
    'kivy.core.image.img_pil',
    'kivy.core.audio.audio_ffpyplayer',
    'kivy.core.video.video_ffpyplayer',

    # ffpyplayer
    'ffpyplayer',
    'ffpyplayer.player',
    'ffpyplayer.pic',
    'ffpyplayer.tools',

    # deps Windows do Kivy
    'kivy_deps.sdl2',
    'kivy_deps.glew',
    'kivy_deps.angle',
]

manual_excludes = [
    # não empacotar testes
    'kivy.tests',
    'pytest',

    # bloquear GStreamer/gstplayer
    'kivy_deps.gstreamer',
    'kivy.core.video.video_gstplayer',
    'kivy.core.audio.audio_gstplayer',
    'kivy.lib.gstplayer',
    'kivy.lib.gstplayer._gstplayer',
]

hiddenimports = kivy_deps.get('hiddenimports', []) + manual_hiddenimports
excludes = kivy_deps.get('excludes', []) + manual_excludes
binaries = kivy_deps.get('binaries', []) + ffpyplayer_binaries
datas = ffpyplayer_datas


a = Analysis(
    ['telas_e_botoes.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=hookspath(),
    hooksconfig={},
    runtime_hooks=['hook_ffpyplayer_only.py'] + runtime_hooks(),
    excludes=excludes,
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
    icon='icone.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,

    # deps Windows do Kivy, sem gstreamer
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + angle.dep_bins)],

    # assets do projeto
    Tree('assets',  prefix='assets'),
    Tree('configs', prefix='configs'),
    Tree('sons',    prefix='sons'),

    strip=False,
    upx=False,
    upx_exclude=[],
    name='Roleta_Quimica',
)
