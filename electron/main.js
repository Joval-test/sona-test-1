const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let backendProcess;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    title: "Caze BizConAI",
    icon: path.join(__dirname, 'app_icon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  win.loadURL('http://localhost:5000/');
  // Optional: Open DevTools for debugging
  // win.webContents.openDevTools();
}

app.whenReady().then(() => {
  // Use process.resourcesPath for packaged apps
  const backendExePath = path.join(
    process.resourcesPath,
    'electron',
    'Caze BizConAI',
    'Caze BizConAI.exe'
  );

  // Start the backend process
  backendProcess = spawn(backendExePath);

  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err);
  });

  backendProcess.stdout && backendProcess.stdout.on('data', (data) => {
    console.log(`[backend]: ${data}`);
  });

  backendProcess.stderr && backendProcess.stderr.on('data', (data) => {
    console.error(`[backend error]: ${data}`);
  });

  // Wait for backend to start, then open the Electron window
  setTimeout(createWindow, 4000);
});

app.on('will-quit', () => {
  if (backendProcess) backendProcess.kill();
});
