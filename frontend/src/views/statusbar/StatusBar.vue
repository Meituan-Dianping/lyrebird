<template>
  <span>
    <span v-for="(item, index) in statusBarList" :key="index" class="main-footer-status">
      <Poptip
        content="content"
        placement="top-start"
        @on-popper-show="getStatusBarDetail(item.id)"
        :width="getPoptipWidth()"
        word-wrap
        padding="10px 20px 10px 20px"
        transfer
      >
        <b class="main-footer-status-button"> {{item.text}}</b>

        <div slot="content">
          <div v-for="(item, index) in statusBarDetail" :key="index">
              <img v-if="item.type=='ImageMenuItem'" :src="item.src" class="image-menu-item">
              <span v-else-if="item.type=='LinkMenuItem'" class="text-menu-item">
                <p class="link-menu-item">
                  <a @click="onClick(item.src.api)">{{item.src.text}}</a>
                </p>
              </span>
              <div v-else class="text-menu-item">{{item.src}}</div>
          </div>
        </div>
      </Poptip>
    </span>
  </span>
</template>

<script>
import { makeRequest } from '@/api'

export default {
  mounted () {
    this.$store.dispatch('loadStatusBarList')
  },
  created () {
    this.$io.on('statusBarUpdate', this.loadStatusBarList)
  },
  destroyed() {
    this.$io.removeListener('statusBarUpdate', this.loadStatusBarList)
  },
  methods: {
    loadStatusBarList () {
      this.$store.dispatch('loadStatusBarList')
    },
    getStatusBarDetail (statusItemId) {
      this.$store.dispatch('loadStatusBarDetail', statusItemId)
    },
    getPoptipWidth () {
      if (!this.statusBarDetail) {
        return 
      }
      for (const item of this.statusBarDetail) {
        if (item.type === 'ImageMenuItem') {
          return 250
        }
      }
    },
    onClick (api) {
      makeRequest(api)
        .then(response => {
          if (response.data && response.data.message) {
            this.$bus.$emit('msg.success', response.data.message)
          }
        })
        .catch(error => {
          this.$bus.$emit('msg.error', error.data.message)
        })
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
.link-menu-item {
  padding:2px 0px;
}
.image-menu-item {
  padding-top: 10px;
  width: 100%;
}
.link-menu-item:hover {
  background-color: #f8f8f9;
}
</style>
