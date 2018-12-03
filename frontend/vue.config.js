const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = {
  configureWebpack: {
    devtool: 'source-map',
    plugins: [
      new MonacoWebpackPlugin()
    ]
  },
  baseUrl: '/static',
  outputDir: '../lyrebird/client/static',
  devServer: {
    proxy: 'http://localhost:9090'
  }
}