module.exports = {
  baseUrl: '/static',
  outputDir: '../lyrebird/client/static',
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:9000'
      },
      '/plugin': {
        target: 'http://localhost:9000'
      }
    }
  }
}
