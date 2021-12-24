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
        primaryLight: '#6A67D4',
        primaryBright: '#7B79D0',

        error: '#FF4B4B',
        warning: '#2d8cf0',
        info: '#ffc107',
        success: '#ff5722',

        accent: '#000520',
        content: '#9B9CB7',

        border: '#F1F0F4',
        shading: '#FAF9FA',
        background: '#FFF'
      },
      dark: {
        primary: '#5F5CCA',
        primaryLight: '#6A67D4',
        primaryBright: '#7B79D0',

        error: '#FF5252',
        warning: '#FB8C00',
        info: '#2196F3',
        success: '#4CAF50',

        accent: '#fff',
        content: '#9B9CB7',

        border: '#F1F0F4',
        shading: '#222222',
        background: '#121212'
      },
    },
  },
}

export default new Vuetify(opts)
