Vue.config.devtools = true;

iview.lang('en-US');

const store = new Vuex.Store({
  state:{

  }
})

const app = new Vue({
    el: '#app',
    store,
    data: {
    },
    components: {
      'data-manager': httpVueLoader('static/vue/datamanager/data-manager.vue')
    }
})