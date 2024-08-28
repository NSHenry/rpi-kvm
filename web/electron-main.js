const { app, BrowserWindow } = require('electron');

function createWindow () {
  const win = new BrowserWindow({
    width: 1280,
    height: 720,
    fullscreen: true,
    icon: '/images/wireless-keyboard-3d.png',
    webPreferences: {
      nodeIntegration: true
    }
  })

  win.loadURL('http://localhost:8080')
}

app.whenReady().then(createWindow)