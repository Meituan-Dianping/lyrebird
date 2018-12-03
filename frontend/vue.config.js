const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = {
  configureWebpack: {
    plugins: [
      new MonacoWebpackPlugin()
    ]
  },
  baseUrl: '/static',
  outputDir: '../lyrebird/client/static',
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:9090'
      },
      '/plugin': {
        target: 'http://localhost:9090'
      },
      '/socket.io': {
        target: 'http://localhost:9090'
      }
    }
  }
}