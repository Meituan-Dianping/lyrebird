<template>
  <span>
    <span v-for="(item, index) in statusBarList" :key="index" class="main-footer-status">
      <Poptip
        content="content"
        placement="top-start"
        width="250"
        word-wrap
        padding="20px 20px 10px 20px"
      >
        <a @click="getStatusBarDetail(item.id)">
          <b class="main-footer-status-button"> {{item.text}}</b>
        </a>
        <div slot="content">
          <div v-for="(item, index) in statusBarDetail" :key="index">
              <img v-if="item.type=='ImageMenuItem'" :src="item.src" style="width:100%">
              <div v-else class="text-menu-item">{{item.src}}</div>
          </div>
        </div>
      </Poptip>
    </span>
  </span>
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

<style scoped>
.text-menu-item {
  font-size: 12px;
  font-weight: bold; 
  color: #808695;
  text-align: center;
  margin-top: 5px;
  word-break: break-all;
}
</style>