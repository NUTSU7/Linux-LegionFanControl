const electron = require('electron');
const url = require('url');
const path = require('path');

const {app, BrowserWindow} = electron;

let mainWindow;

app.on('ready', function()
{
    mainWindow = new BrowserWindow({
        autoHideMenuBar: true,
        width: 1000, height: 800,
        icon: `${__dirname}/assets/img/main.png`
});

    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, '/src/mainWindow.html'),
        protocol: 'file:',
        slashes: true
    }));
    // Quit app when closed
    mainWindow.on('closed', function () {
        app.quit();
    });

});
