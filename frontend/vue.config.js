const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')

module.exports = {
  configureWebpack: {
    devtool: 'source-map',
    plugins: [new MonacoWebpackPlugin()],
  },
  transpileDependencies: ['lossless-json'],
  publicPath: '/ui/static',
  productionSourceMap: false,
  outputDir: '../lyrebird/client/static',
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:9090', // 使用 IP 地址替代 localhost
        changeOrigin: true,
        ws: true,
        pathRewrite: {
          '^/api': '/api'
        }
      },
      '/*plugin*': {
        target: 'http://127.0.0.1:9090',
        changeOrigin: true
      },
      '/static': {
        target: 'http://127.0.0.1:9090',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://127.0.0.1:9090',
        changeOrigin: true,
        ws: true
      }
    },
    host: '127.0.0.1',
    port: 8080,
    https: false
  },
}
