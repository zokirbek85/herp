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
- `pytz` — bizning kodimizda hech qayerda `import pytz` yo'q, lekin DuckDB'ning C kengaytmasi
  ba'zi sana/vaqt amallarida uni runtime'da ichkaridan dinamik import qiladi. modulegraph buni
  ko'ra olmaydi, shu sababli qo'lda `hiddenimports`ga qo'shilgan (aks holda
  "Required module 'pytz' failed to import" xatosi chiqadi).
"""

import sys

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
    hiddenimports=["duckdb_engine", "logging.config", "pytz"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

# macOS'da onefile EXE + `.app` BUNDLE birgalikda PyInstaller tomonidan eskirgan deb topiladi
# (v7'da xato bo'ladi) — shu sababli macOS uchun onedir (`exclude_binaries` + `COLLECT`) qo'llanadi,
# Windows uchun esa avvalgidek yagona EXE saqlanadi.
if sys.platform == "darwin":
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="HazoraspSalesManagement",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name="HazoraspSalesManagement",
    )
    app = BUNDLE(
        coll,
        name="HazoraspSalesManagement.app",
        bundle_identifier="uz.hazorasptekstil.salesmanagement",
        info_plist={
            "CFBundleName": "Hazorasp Sales Management",
            "CFBundleDisplayName": "Hazorasp Sales Management",
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleVersion": "0.1.0",
            "NSHighResolutionCapable": True,
        },
    )
else:
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
