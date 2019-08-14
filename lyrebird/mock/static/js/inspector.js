Vue.config.devtools = true;

iview.lang('en-US');

const app = new Vue({
    el: '#app',
    store,
    data: {
    },
    components: {
      'inspector': httpVueLoader('static/vue/inspector.vue')
    }
})
