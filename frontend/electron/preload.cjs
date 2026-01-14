const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // 暴露选择文件夹的方法
  selectFolder: () => ipcRenderer.invoke('dialog:openDirectory')
})