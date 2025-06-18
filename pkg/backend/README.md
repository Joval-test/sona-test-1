# Caze BizConAI Application

## Antivirus Information

If your antivirus software flags the application, this is likely a false positive. The application is created using PyInstaller, which bundles Python applications into standalone executables. Some antiviruses may flag PyInstaller-generated executables due to their packaging method.

To resolve this:

1. Add an exception in your antivirus software for:
   - The Caze BizConAI installation folder
   - The executable file (Caze BizConAI.exe)

2. Alternative solutions:
   - Run the application from source code instead of the executable
   - Use Windows Defender instead of third-party antivirus (typically has fewer false positives with PyInstaller)
   - Download from trusted source only (your official distribution channel)

## Why is this happening?

- PyInstaller bundles Python code and dependencies into a single executable
- This bundling process can trigger heuristic detection in some antivirus software
- The application is not signed with a digital certificate (common for internal/small-scale applications)

## Security Assurance

- The source code is available for inspection
- The application is built using standard Python libraries and frameworks
- No malicious code or unauthorized data collection is included
