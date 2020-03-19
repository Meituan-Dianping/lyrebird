<template>
  <div id="statusBar">
    <span v-for="(item, index) in statusBarList" :key="index">
      <Poptip
        content="content"
        placement="top-start"
        width="250"
        style="margin-right:5px;"
        word-wrap
      >
        <a @click="getStatusBarDetail(item.id)">
          <b style="color:#f8f8f9"> {{item.text}}</b>
          <Icon type="ios-arrow-dropup-circle" style="color:#f8f8f9;margin-left:5px;"/>
        </a>
        <div slot="content">
          <div v-for="(item, index) in statusBarDetail" :key="index">
              <img v-if="item.type=='ImageMenuItem'" :src="item.src" style="width:100%">
              <div v-else >{{item.src}}</div>
          </div>
        </div>
      </Poptip>
    </span>
  </div>
</template>

<script>
export default {
  mounted () {
    this.$store.dispatch('loadStatusBarList')
  },
  methods: {
    getStatusBarDetail (statusItemId) {
      this.$store.dispatch('loadStatusBarDetail', statusItemId)
    }
  },
  computed: {
    statusBarList () {
      return this.$store.state.statusbar.statusBarList
    },
    statusBarDetail () {
      return this.$store.state.statusbar.statusBarDetail
    },
  }
}
</script>

<style  scoped>
#statusBar {
  width: 600px;
  display: inline-block;
}
</style>
