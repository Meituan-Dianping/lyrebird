<template>
  <div id="status-bar">
    <span v-for="(item, index) in statusBarList" :key="index">
      <Poptip
        content="content"
        placement="top-start"
        width="250"
        style="margin-right:20px;"
        word-wrap
        padding="20px 20px 10px 20px"
      >
        <a @click="getStatusBarDetail(item.id)">
          <b style="color:#f8f8f9;font-size:12px;"> {{item.text}}</b>
        </a>
        <div slot="content">
          <div v-for="(item, index) in statusBarDetail" :key="index">
              <img v-if="item.type=='ImageMenuItem'" :src="item.src" style="width:100%">
              <div v-else class="text-menu-item">{{item.src}}</div>
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
#status-bar {
  width: 600px;
  display: inline-block;
}
.text-menu-item {
  font-size: 14px;
  font-weight: bold; 
  color: #808695;
  text-align: center;
  margin-top: 5px;
}
</style>
