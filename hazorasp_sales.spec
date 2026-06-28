# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: Hazorasp Sales Management.

Build: pyinstaller hazorasp_sales.spec

Diqqat:
- `alembic/` va `alembic.ini` runtime'da kerak (app.database.migrations.run_upgrade_to_head
  ularni `sys._MEIPASS` ichidan o'qiydi — shu fayl tuzilishi shu yerda saqlanishi shart).
- `duckdb_engine` SQLAlchemy dialektini setuptools entry_points orqali ro'yxatdan o'tkazadi —
  bu metadata kodning o'zi emas, shuning uchun `copy_metadata` orqali alohida bundle qilinadi,
  aks holda runtime'da "Can't load plugin: sqlalchemy.dialects:duckdb" xatosi chiqadi.
- `qtawesome` icon shriftlari (`fonts/*.ttf`) paket ichidagi data fayllar — modulegraph ularni
  avtomatik aniqlamaydi, shu sababli `collect_data_files` bilan qo'lda qo'shiladi.
"""

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = [
    ("alembic", "alembic"),
    ("alembic.ini", "."),
]
datas += collect_data_files("qtawesome")
datas += copy_metadata("duckdb_engine")

a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    # "logging.config" — `alembic/env.py` runtime'da fayldan o'qib exec qilinadi
    # (`alembic.util.pyfiles.load_module_py`), shu sababli uning importlari PyInstaller'ning
    # statik modulegraph tahlilida ko'rinmaydi va qo'lda ko'rsatilishi shart.
    hiddenimports=["duckdb_engine", "logging.config"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="HazoraspSalesManagement",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
)
