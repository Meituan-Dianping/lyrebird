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
    proxy: 'http://localhost:9090'
  },
  configureWebpack: {
    devtool: 'source-map'
  }
}