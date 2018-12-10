const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = {
  configureWebpack: {
    devtool: 'source-map',
    plugins: [
      new MonacoWebpackPlugin()
    ]
  },
  baseUrl: '/ui/static',
  outputDir: '../lyrebird/client/static',
  devServer: {
    proxy: {
      '/api': {
          target: 'http://localhost:9090'
      },
      '/plugin': {
          target: 'http://localhost:9090'
      },
      '/static': {
         target: 'http://localhost:9090'
      },
      '/socket.io': {
        target: 'http://localhost:9090'
      }
  }
  }
}