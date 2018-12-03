module.exports = {
  baseUrl: '/static',
  outputDir: '../lyrebird/client/static',
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:9090'
      },
      '/plugin': {
        target: 'http://localhost:9090'
      }
    }
  },
  configureWebpack: {
    devtool: 'source-map'
  }
}
