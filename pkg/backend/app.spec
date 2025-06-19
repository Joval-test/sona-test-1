# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all, copy_metadata

block_cipher = None

# Paths
resources_path = os.path.join('..','..', '.venv', 'Lib', 'site-packages', 'docling_parse', 'pdf_resources_v2')
icon_path = os.path.abspath(os.path.join(SPECPATH, 'app_icon.ico'))
frontend_path = os.path.abspath(os.path.join(SPECPATH, '..', 'frontend', 'build'))

# Data collection for required packages (excluding .py files)
def filter_py_files(data_list):
    return [(src, tgt) for src, tgt in data_list if not src.endswith('.py') and not src.endswith('.pyc')]

docling_data = collect_all('docling')
easyocr_data = collect_all('easyocr')
torch_data = collect_all('torch')

# Static dashboard templates
mpire_dashboard_templates = collect_data_files('mpire', subdir='dashboard/templates')

# Combine all data files
all_datas = []
all_datas += filter_py_files(docling_data[0])
all_datas += filter_py_files(easyocr_data[0])
all_datas += filter_py_files(torch_data[0])
all_datas += copy_metadata('torch')
all_datas += copy_metadata('torchvision')
all_datas += copy_metadata('easyocr')
all_datas += copy_metadata('transformers')
all_datas += copy_metadata('huggingface-hub')
all_datas += copy_metadata('safetensors')
all_datas += [
    (frontend_path, 'frontend/build'),
    ('logging_utils.py', '.'),
    ('config.py','.'),
    ('logo_transparent.png', '.'),
    *mpire_dashboard_templates,
    (resources_path, 'docling_parse/pdf_resources_v2'),
]

# Combine all binaries
all_binaries = []
all_binaries += docling_data[1]
all_binaries += easyocr_data[1]
all_binaries += torch_data[1]

# Combine all hidden imports
all_hiddenimports = []
all_hiddenimports += docling_data[2]
all_hiddenimports += easyocr_data[2]
all_hiddenimports += torch_data[2]
all_hiddenimports += [
    # Specific Docling OCR engine imports
    'docling.datamodel.pipeline_options',
    'docling.datamodel.base_models',
    'docling.backend.docling_parse_backend',
    'docling.backend.pypdfium2_backend',

    # EasyOCR specific modules
    'easyocr.easyocr',
    'easyocr.recognition',
    'easyocr.detection',
    'easyocr.model.model',

    # PyTorch essentials
    'torch._C',
    'torch._utils_internal',
    *collect_submodules('tiktoken'),
    # Langchain/ChromaDB
    *collect_submodules('langchain_chroma'),
    *collect_submodules('langchain_openai'),
    'chromadb.telemetry.product.posthog',
    'chromadb.api.rust',
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
]

a = Analysis(
    ['app.py'],
    pathex=['.', '../', '../../'],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
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
    name='Caze BizConAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
