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
        accent: '#000520',
        error: '#FF4B4B',
        warning: '#2d8cf0',
        info: '#ffc107',
        success: '#ff5722',
        shading: '#FAF9FA',
        background: '#FFF'
      },
      dark: {
        primary: '#5F5CCA',
        secondary: '#424242',
        accent: '#fff',
        error: '#FF5252',
        warning: '#FB8C00',
        info: '#2196F3',
        success: '#4CAF50',
        shading: '#222222',
        background: '#121212'
      },
    },
  },
}

export default new Vuetify(opts)
