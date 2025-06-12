# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules
import os
resources_path = os.path.join('..','..','.venv', 'Lib', 'site-packages', 'docling_parse', 'pdf_resources_v2')

# Get icon path
icon_path = os.path.abspath(os.path.join(SPECPATH, 'app_icon.ico'))

langchain_docling = collect_all('langchain_docling')
langchain_chroma = collect_all('langchain_chroma')
easyocr_data, easyocr_binaries, easyocr_hidden = collect_all('easyocr')
docling_data, docling_binaries, docling_hidden = collect_all('docling')
langchain_openai = collect_all('langchain_openai')

# Helper to flatten collect_all output for datas
def flatten_collect_all(collect_all_result, dest_folder):
    datas, binaries, hiddenimports = collect_all_result
    return [(src, os.path.join(dest_folder, dest)) for src, dest in datas]

# Add mpire dashboard templates to datas
mpire_dashboard_templates = collect_data_files('mpire', subdir='dashboard/templates')

# Get absolute path to frontend build directory
frontend_path = os.path.abspath(os.path.join(SPECPATH, '..', 'frontend', 'build'))

a = Analysis(
    ['app.py'],
    pathex=['.', '../', '../../'],
    binaries=[
        *easyocr_binaries,
        *docling_binaries,
        # Add your compiled modules here
        ('core/*.pyd', 'core'),  # For Windows
        # ('core/*.so', 'core'),  # For Linux/Mac
    ],
    datas=[
        # Add frontend directory as a single unit
        (frontend_path, 'frontend/build'),
        # ('core', 'core'),
        ('logging_utils.py', '.'),
        ('logo_transparent.png', '.'),  # Add logo to root of executable
        *flatten_collect_all(langchain_docling, 'langchain_docling'),
        *flatten_collect_all(langchain_chroma, 'langchain_chroma'),
        *flatten_collect_all(langchain_openai, 'langchain_openai'),
        *easyocr_data,
        (resources_path, 'docling_parse/pdf_resources_v2'),
        *docling_data,
        *mpire_dashboard_templates,
    ],
    hiddenimports=[
        *collect_submodules('easyocr'),
        *collect_submodules('docling'),
        'chromadb.telemetry.product.posthog',
        'chromadb.api.rust',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure)

# Create the EXE
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Caze BizConAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Caze BizConAI',
)
