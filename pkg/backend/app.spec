# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files
import os

chromadb=collect_all('chromadb')
langchain_docling = collect_all('langchain_docling')
langchain_chroma = collect_all('langchain_chroma')
langchain_openai = collect_all('langchain_openai')

# Helper to flatten collect_all output for datas
def flatten_collect_all(collect_all_result, dest_folder):
    datas, binaries, hiddenimports = collect_all_result
    return [(src, os.path.join(dest_folder, dest)) for src, dest in datas]

# Add mpire dashboard templates to datas
mpire_dashboard_templates = collect_data_files('mpire', subdir='dashboard/templates')

# Get absolute path to frontend build directory
frontend_path = os.path.abspath(os.path.join(SPECPATH, '..', 'frontend', 'build'))
logo_path = os.path.abspath(os.path.join(SPECPATH, '..', 'frontend', 'public', 'images', 'logo_transparent.png'))

a = Analysis(
    ['app.py'],
    pathex=['.', '../', '../../'],
    binaries=[],
    datas=[
        # Add frontend directory as a single unit
        (frontend_path, 'frontend/build'),
        (logo_path, '.'),
        ('core', 'core'),
        ('logging_utils.py', '.'), 
        *flatten_collect_all(chromadb, 'chromadb'),    
        *flatten_collect_all(langchain_chroma, 'langchain_chroma'),
        *flatten_collect_all(langchain_docling, 'langchain_docling'),
        *flatten_collect_all(langchain_openai, 'langchain_openai'),
        *mpire_dashboard_templates,
        ('logo_transparent.png', '.'), 
    ],
    hiddenimports=['chromadb.telemetry.product.posthog', 'chromadb.api.rust'],
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
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
