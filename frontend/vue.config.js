const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = {
  lintOnSave: process.env.NODE_ENV !== 'production',
  configureWebpack: {
    devtool: 'source-map',
    plugins: [
      new MonacoWebpackPlugin()
    ]
  },
  publicPath: '/ui/static',
  productionSourceMap: false,
  outputDir: '../lyrebird/client/static',
  devServer: {
    overlay: {
      warnings: true,
      errors: true
    },
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