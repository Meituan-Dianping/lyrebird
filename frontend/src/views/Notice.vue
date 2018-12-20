<template>
    <div>
      {{data.message}}
      <p>
        <b><a href="#" @click="jump(data)">Create new issue</a></b>
      </p>
    </div>
</template>

<script>
  import store from '../store/index'
  import router from '../router'

  export default {
    name: 'notice',
    props: ["data"],
    data() {
      return {
        jumpUrl: null
      }
    },
    mounted() {
    },
    methods: {
      jump(data) {
        // TODO: support select manifest
        // store.state.manifest[0]: only one manifest are supported in v1.0
        for(const menuItem of store.state.menu){
          if (menuItem['params'] && store.state.manifest[0] === menuItem['params']['name']){
            store.commit('setActiveName', menuItem.title)
            this.jumpUrl = menuItem['params']['src']
            break
          }
        }
        store.commit('plugin/setSrc', this.jumpUrl);
        router.push({name:'plugin-view', param:this.jumpUrl});
      }
    }
  };
</script>

<style>
</style>
    