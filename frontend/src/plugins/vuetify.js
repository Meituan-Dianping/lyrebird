// src/plugins/vuetify.js

import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

Vue.use(Vuetify)

const opts = {
    breakpoint: {
        scrollBarWidth: 16,
        thresholds: {
          xs: 600,
          sm: 960,
          md: 1280,
          lg: 1920,
        },
    },
    icons: {
        iconfont: 'mdi',
        values: {},
    },
    theme: {
        dark: true,
        default: 'light',
        disable: false,
        themes: {
          light: {
            primary: '#2196F3',
            secondary: '#424242',
            accent: '#FF4081',
            error: '#FF5252',
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FB8C00',
          },
          dark: {
            primary: '#1976D2',
            secondary: '#424242',
            accent: '#82B1FF',
            error: '#FF5252',
            info: '#2196F3',
            success: '#4CAF50',
            warning: '#FB8C00',
          },
        },
      },
}

export default new Vuetify(opts)