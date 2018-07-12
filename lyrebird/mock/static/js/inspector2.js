Vue.config.devtools = true;

iview.lang('en-US');

new Vue({
    el: '#app',
    data: {
    },
    components: {
      'inspector': httpVueLoader('static/vue/inspector.vue')
    }
})