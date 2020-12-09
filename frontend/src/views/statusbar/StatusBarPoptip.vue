<template>
  <Poptip
    v-model="shown"
    content="content"
    placement="top-start"
    width="250"
    style="margin-right:20px;"
    word-wrap
    padding="20px 20px 10px 20px"
  >
    <a @click="getStatusBarDetail(bar.id)">
      <b style="color:#f8f8f9;font-size:12px;"> {{bar.text}}</b>
    </a>
    <div slot="content">
      <div v-for="(item, index) in statusBarDetail" :key="index">
        <img v-if="item.type=='ImageMenuItem'" :src="item.src" style="width:100%">
        <div v-else class="text-menu-item">{{item.src}}</div>
      </div>
    </div>
  </Poptip>
</template>

<script>
export default {
  props: ['barIndex'],
  data () {
    return {
      shown: false
    }
  },
  computed: {
    bar () {
      return this.$store.state.statusbar.statusBarList[this.barIndex]
    },
    statusBarDetail () {
      return this.$store.state.statusbar.statusBarDetail
    },
    visible: {
      get () {
        return this.$store.state.statusbar.statusBarList[this.barIndex].shown
      },
      set (val) {
        this.$store.commit('setStatusBarListItem', { key: this.infoKey, value: val })
        this.shown = val
        this.getStatusBarDetail(this.bar.id)
      }
    }
  },
  methods: {
    getStatusBarDetail (statusItemId) {
      this.$store.dispatch('loadStatusBarDetail', statusItemId)
    }
  }
}
</script>
