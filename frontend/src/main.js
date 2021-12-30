import '@mdi/font/css/materialdesignicons.css'
import Vue from 'vue'
import store from './store/index'
import iView from 'iview'
import vuetify from '@/plugins/vuetify'
import VueResource from 'vue-resource'
import 'iview/dist/styles/iview.css'
import locale from 'iview/dist/locale/en-US'
import io from 'socket.io-client'
import { bus } from './eventbus'
import VueClipboard from 'vue-clipboard2'
import App from './App.vue'

// Import router must be put after 'iview/dist/styles/iview.css'
import router from './router'


Vue.config.productionTip = false
Vue.use(iView, { locale })
Vue.use(VueResource)
Vue.use(VueClipboard)

Vue.prototype.$io = io()
Vue.prototype.$bus = bus

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

// Disable broswer swipe forward and backward
window.addEventListener('popstate', function() {
  history.pushState(null, null, document.URL)
})
