# -*- mode: python ; coding: utf-8 -*-
# --onedir mode: no self-extraction to %%TEMP%%.
# Reduces Windows Defender ML heuristic score by avoiding temp-extraction pattern.


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('insumos', 'insumos'), ('equipos', 'equipos'), ('Theme', 'Theme')],
    hiddenimports=[
        'openpyxl', 'openpyxl.styles', 'openpyxl.utils',
        'PIL', 'PIL.Image', 'PIL.ImageTk',
        'PyQt5', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.sip',
        'fpdf',
        'path_config',
        'tkinter', 'tkinter.ttk', 'tkinter.simpledialog', 'tkinter.filedialog',
        'xml.etree.ElementTree', 'xml.etree.cElementTree', 'et_xmlfile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'test', 'pydoc', 'distutils', 'json.tool', 'lib2to3', 'multiprocessing', 'pdb', 'pickle', 'pydoc_data', 'sqlite3', 'telnetlib', 'turtle', 'turtledemo', 'venv', 'webbrowser', 'xmlrpc'],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='launcher',
    debug=False,
    version='file_version.txt',
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Theme\\app_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=False,
    upx_exclude=[],
    name='launcher',
)
