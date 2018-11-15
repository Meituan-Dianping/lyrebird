import Vue from 'vue'
import iView from 'iview'
import App from './App.vue'
import store from './store'
import 'iview/dist/styles/iview.css';
import router from './router'
import VueResource from 'vue-resource';


Vue.config.productionTip = false
Vue.use(iView)
Vue.use(VueResource)

new Vue({
  store,
  router,
  render: h => h(App)
}).$mount('#app')
