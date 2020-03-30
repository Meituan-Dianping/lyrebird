import Vue from 'vue'
import App from './App.vue'
import store from './store'
import ViewUI from 'view-design'
import 'view-design/dist/styles/iview.css'
import io from 'socket.io-client'

Vue.config.productionTip = false

Vue.use(ViewUI)
Vue.prototype['$io'] = io()

new Vue({
  store,
  render: h => h(App)
}).$mount('#app')
