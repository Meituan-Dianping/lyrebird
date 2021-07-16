import Vue from 'vue'
import Router from 'vue-router'
import Main from './views/Main.vue'
import Inspector from './views/inspector/Inspector.vue'
import DataManager from './views/datamanager/DataManager.vue'
import Checker from './views/checker/Checker.vue'
import PluginView from './views/PluginView.vue'

Vue.use(Router)

export default new Router({
  // Disable broswer swipe forward and backward
  scrollBehavior: () => {
    history.pushState(null, null, document.URL)
  },
  routes: [
    {
      path: '/',
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
      component: Main,
      children: [
        {
          path: '',
          name: 'datamanager',
          component: DataManager
        },
        {
          path: 'import',
          name: 'datamanagerImport',
          component: DataManager,
        },
      ]
    },
    {
      path: '/checker',
      component: Main,
      children: [
        {
          path: '',
          name: 'checker',
          component: Checker
        }
      ]
    },
    {
      path: '/plugin',
      name: 'plugin',
      component: Main,
      children: [
        {
          path: ':name',
          name: 'plugin-view',
          component: PluginView
        }
      ]
    },
    {
      path: '/plugins',
      name: 'plugins',
      component: Main,
      children: [
        {
          path: ':name',
          name: 'plugin-container',
          component: PluginView
        }
      ]
    }
  ]
})
