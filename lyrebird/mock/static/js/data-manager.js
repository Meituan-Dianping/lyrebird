Vue.config.devtools = true;

Vue.prototype.$api = api

iview.lang('en-US');


const app = new Vue({
    el: '#app',
    store,
    data: {
    },
    components: {
      'data-manager': httpVueLoader('static/vue/datamanager/data-manager.vue')
    }
})