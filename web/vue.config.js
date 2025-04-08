const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://192.168.165', // The target API server
        changeOrigin: true, // Required for virtual hosted sites
        pathRewrite: { '^/api': '' }, // Rewrite path (optional)
      }
    }
  }
})