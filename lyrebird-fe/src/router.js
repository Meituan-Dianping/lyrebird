import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Inspector from './views/inspector/inspector.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/inspector',
      name: 'inspector',
      component: Inspector
    },
    {
      path: '/hello',
      name: 'hello',
      component: () => import(/* webpackChunkName: "about" */ './views/Hello.vue')
    },
  ]
})
