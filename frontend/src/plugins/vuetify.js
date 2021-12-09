import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'


Vue.use(Vuetify)

const opts = {
  icons: {
      iconfont: 'mdi',
      values: {},
  },
  theme: {
    dark: false,
    default: 'light',
    disable: false,
    themes: {
      light: {
        primary: '#5F5CCA',
        secondary: '#515a6e',
        accent: '#000',
        error: '#03a9f4',
        warning: '#2d8cf0',
        info: '#ffc107',
        success: '#ff5722'
      },
      dark: {
        primary: '#5F5CCA',
        secondary: '#424242',
        accent: '#fff',
        error: '#FF5252',
        warning: '#FB8C00',
        info: '#2196F3',
        success: '#4CAF50',
      },
    },
  },
}

export default new Vuetify(opts)
