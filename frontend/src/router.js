import Vue from 'vue'
import Router from 'vue-router'
import Main from './views/Main.vue'
import Inspector from './views/inspector/Inspector.vue'
import DataManager from './views/datamanager/DataManager.vue'
import PluginView from './views/PluginView.vue'


Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: '_inspector',
      component: Main,
      children: [
        {
          path: '',
          name: 'inspector',
          component: Inspector
        }
      ]
    },
    {
      path: '/datamanager',
      name: '_datamanager',
      component: Main,
      children: [
        {
          path:'',
          name: 'datamanager',
          component: DataManager
        }
      ]
    },
    {
      path: '/plugin',
      name: 'plugin',
      component: Main,
      children:[
        {
          path:'/:name',
          name: 'plugin-view',
          component: PluginView
        }
      ]
    }
  ]
})
