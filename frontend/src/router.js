import Vue from 'vue'
import Router from 'vue-router'
import Main from './views/Main.vue'
import Inspector from './views/inspector/Inspector.vue'
import DataManager from './views/datamanager/DataManager.vue'
import Checker from './views/checker/Checker.vue'
import EventInspector from '@/views/event/EventInspector.vue'
import PluginView from './views/PluginView.vue'
import Settings from './views/settings/Settings.vue'

//vue router error handler
const originalPush = Router.prototype.push
Router.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(error => {
    if (error.name !== 'NavigationDuplicated') {
      console.log('Router error: ', error)
    } else {
      console.log('Router error: NavigationDuplicated ', location)
    }
  })
}

Vue.use(Router)

export default new Router({
  // Disable broswer swipe forward and backward
  scrollBehavior: () => {
    history.pushState(null, null, document.URL)
  },
  mode: 'hash',
  routes: [
    {
      path: '/',
      component: Main,
      children: [
        {
          path: '',
          name: 'inspector',
          component: Inspector,
        },
      ],
    },
    {
      path: '/datamanager',
      component: Main,
      children: [
        {
          path: '',
          name: 'datamanager',
          component: DataManager,
        },
        {
          path: 'import',
          name: 'datamanagerImport',
          component: DataManager,
        },
      ],
    },
    {
      path: '/checker',
      component: Main,
      children: [
        {
          path: '',
          name: 'checker',
          component: Checker,
        },
      ],
    },
    {
      path: '/inspector-pro',
      component: Main,
      children: [
        {
          path: '',
          name: 'inspector-pro',
          component: EventInspector,
        },
      ],
    },
    {
      path: '/settings',
      component: Main,
      children: [
        {
          path: '',
          name: 'settings',
          component: Settings,
        },
      ],
    },
    {
      path: '/plugin',
      name: 'plugin',
      component: Main,
      children: [
        {
          path: ':name',
          name: 'plugin-view',
          component: PluginView,
        },
      ],
    },
    {
      path: '/plugins',
      name: 'plugins',
      component: Main,
      children: [
        {
          path: ':name',
          name: 'plugin-container',
          component: PluginView,
        },
      ],
    },
  ],
})
