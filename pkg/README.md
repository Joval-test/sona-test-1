# BizCon Flask + React Scaffold

## Setup Instructions

### 1. Backend (Flask)

```bash
cd pkg/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 2. Frontend (React)

```bash
cd pkg/frontend
npm install
npm start
```

- The React app runs on port 3000 (dev), Flask on 5000.
- For API calls in development, you may need to adjust the fetch URLs or use a proxy.

### 3. Production Build

- Build the React app:
  ```bash
  npm run build
  ```
- Move/copy the `build/` folder to `../frontend/build` if not already there.
- Run Flask (`python app.py`). It will serve the React app on `/` and API on `/api/*`.

### 4. Packaging as EXE

- Use PyInstaller on `app.py` to create an exe:
  ```bash
  pyinstaller --onefile app.py
  ```
- Make sure the `build/` folder is included with the exe or bundled as data.

---

## Next Steps
- Add your business logic and endpoints to `backend/app.py`.
- Build out your React components in `frontend/src/components/`.
- Migrate features from your Streamlit app to this new stack. 