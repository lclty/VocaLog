const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')

// 屏蔽安全警告
process.env.ELECTRON_DISABLE_SECURITY_WARNINGS = 'true'

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      // 预加载脚本，用于建立 Vue 和 Electron 的桥梁
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  // 开发环境加载 Vue 服务，生产环境加载打包文件
  // 注意：这里假设 Vue 运行在 5173 端口，如果你的端口不同请修改
  const devUrl = 'http://localhost:5173'
  
  // 在本地调试阶段，我们让 Electron 直接加载 Vue 的开发服务器
  win.loadURL(devUrl).catch(() => {
    console.log('Vue dev server not ready yet?')
  })

  // win.webContents.openDevTools() // 如果需要调试控制台请解注
}

// --- IPC 监听：处理选择文件夹请求 ---
ipcMain.handle('dialog:openDirectory', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openDirectory']
  })
  if (canceled) {
    return null
  } else {
    return filePaths[0] // 返回绝对路径
  }
})

app.whenReady().then(() => {
  createWindow()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})