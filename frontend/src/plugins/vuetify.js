// src/plugins/vuetify.js

import Vue from 'vue'
import Vuetify from 'vuetify'
//import Vuetify from'vuetify/lib'
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
        primary: '#2d8cf0',
        secondary: '#515a6e',
        accent: '#000',
        error: '#03a9f4',
        warning: '#2d8cf0',
        info: '#ffc107',
        success: '#ff5722'
      },
      dark: {
        primary: '#1976D2',
        secondary: '#424242',
        accent: '#fff',
        error: '#FF5252',
        info: '#2196F3',
        success: '#4CAF50',
        warning: '#FB8C00',
      },
    },
  },
}

export default new Vuetify(opts)