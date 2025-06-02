# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all, copy_metadata

# Collect dependencies
chromadb_data, chromadb_binaries, chromadb_hidden = collect_all('chromadb')
tiktoken_data, tiktoken_binaries, tiktoken_hidden = collect_all('tiktoken')
easyocr_data, easyocr_binaries, easyocr_hidden = collect_all('easyocr')
docling_data, docling_binaries, docling_hidden = collect_all('docling')

# Define the path to docling resources
resources_path = os.path.join('.', '../', '../', '.venv', 'Lib', 'site-packages', 'docling_parse', 'pdf_resources_v2')

# Define frontend build path - for pkg/backend structure
frontend_build_path = '../frontend/build'

# Verify frontend build exists
if not os.path.exists(frontend_build_path):
    print(f"WARNING: Frontend build path does not exist: {frontend_build_path}")
    print("Make sure to run 'npm run build' in your frontend directory first!")
else:
    print(f"Frontend build found at: {frontend_build_path}")

a = Analysis(
    ['app.py'],
    pathex=['.', '../', '../../', 'D:/Projects/Caze_IC_Caller_AI/.venv/Lib/site-packages'],
    binaries=[
        *chromadb_binaries,
        *tiktoken_binaries,
        *easyocr_binaries,
        *docling_binaries,
    ],
    datas=[
        # Core application files
        ('core', 'core'),
        ('logging_utils.py', '.'),
        
        # Frontend build files - this is the key fix
        (frontend_build_path, 'frontend/build'),
        
        # Dependencies data
        *chromadb_data,
        *copy_metadata('chromadb'),
        *tiktoken_data,
        *easyocr_data,
        *docling_data,
        
        # Additional dependencies
        ('D:/Projects/Caze_IC_Caller_AI/.venv/Lib/site-packages/langchain_docling', 'langchain_docling'),
        ('D:/Projects/Caze_IC_Caller_AI/.venv/Lib/site-packages/mpire/dashboard/templates', 'mpire/dashboard/templates'),
        (resources_path, 'docling_parse/pdf_resources_v2'),
    ],
    hiddenimports=[
        # Hidden imports for all dependencies
        *tiktoken_hidden,
        *easyocr_hidden,
        *docling_hidden,
        *chromadb_hidden,
        *collect_submodules('torch'),
        *collect_submodules('chromadb'),
        *collect_submodules('tiktoken'),
        *collect_submodules('easyocr'),
        *collect_submodules('docling'),
        
        # Specific imports
        'langchain_docling',
        'chromadb.telemetry.product.posthog',
        'chromadb.api.rust',
        'langchain',
        'langchain.prompts',
        'langchain_chroma',
        'langchain_openai',
        'langchain_ollama',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        'dotenv',
        'torch',
        'torch._C',
        'torch.classes',
        'torch.distributed',
        'torch.distributed.nn',
        'torch.distributed.nn.jit',
        'chromadb.db.base',
        'chromadb.utils.embedding_functions',
        'chromadb.utils.embedding_functions.onnx_model',
        'chromadb.utils.embedding_functions.sentence_transformer'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)