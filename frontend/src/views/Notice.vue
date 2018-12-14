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
      }
    },
    mounted() {
    },
    methods: {
      jump(data) {
        // TODO: support select manifest
        // let url = '/plugin/'+ store.state.manifest + '?eventId=' + data.id
        let url = '/plugin/'+ store.state.manifest[0] + '?eventId=' + data.id
        store.commit('plugin/setSrc', url);
        router.push({name:'plugin-view', param:url});
        
      }
    }
  };
</script>

<style>
</style>
    