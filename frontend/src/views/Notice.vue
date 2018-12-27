<template>
    <div>
      <div style="padding-right:15px;word-break:break-all">
          {{noticeInfo.message}}
      </div>
      <p>
        <b><a href="#" @click="jump(noticeInfo)">Create new issue</a></b>
      </p>
    </div>
</template>

<script>
  import store from '../store/index'
  import router from '../router'

  export default {
    name: 'notice',
    props: ["noticeInfo"],
    data() {
      return {
        jumpToUrl: null,
        jumpToName: null
      }
    },
    mounted() {
    },
    methods: {
      jump(noticeInfo) {
        // TODO: support select manifest
        // store.state.manifest[0]: only one manifest are supported in v1.0
        for(const menuItem of store.state.menu){
          if (menuItem['params'] && store.state.manifest[0] === menuItem['params']['name']){
            store.commit('setActiveName', menuItem.title)
            this.jumpToUrl = menuItem.params.src
            this.jumpToName = menuItem.params.name
            break
          }
        }
        store.commit('plugin/setSrc', this.jumpToUrl)
        router.push({name:'plugin-view', params:{name:this.jumpToName}})
        store.dispatch("createIssue", noticeInfo)
      }
    }
  };
</script>

<style>
</style>
    