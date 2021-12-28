<template>
  <span>
    <span class="main-footer-status-placeholder"/>

    <span class="main-footer-status" v-show="activatedGroupName">
      <v-tooltip top>
        <template v-slot:activator="{ on, attrs }">
          <span
            v-bind="attrs"
            v-on="on"
            class="main-footer-status-button"
            @click="resetActivatedData"
            style="cursor:pointer;"
          >
            <b >Mock group {{activatedGroupName}}</b>
          </span>
        </template>
        <span>Click to deactivate</span>
      </v-tooltip>
    </span>

    <span v-for="(item, index) in statusBottomLeftList" :key="index" class="main-footer-status">
      <Poptip
        content="content"
        placement="top-start"
        @on-popper-show="getStatusBarDetail(item.name)"
        :width="getPoptipWidth()"
        word-wrap
        padding="10px 20px 10px 20px"
        transfer
      >
        <b class="main-footer-status-button">
          <v-icon v-if="item.prepend_icon" small color="white">
            {{item.prepend_icon}}
          </v-icon>
          {{item.text}}
        </b>

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
  created () {
    this.$io.on('activatedGroupUpdate', this.loadActivatedGroup)
  },
  beforeDestroy () {
    this.$io.removeListener('activatedGroupUpdate', this.loadActivatedGroup)
  },
  
  computed: {
    statusBottomLeftList () {
      return this.$store.state.statusbar.statusBottomLeftList
    },
    statusBottomRightList () {
      return this.$store.state.statusbar.statusBottomRightList
    },
    statusBarDetail () {
      return this.$store.state.statusbar.statusBarDetail
    },
    activatedGroupName () {
      const activatedGroups = this.$store.state.inspector.activatedGroup
      if (activatedGroups === null) {
        return null
      }
      if (Object.keys(activatedGroups) === 0) {
        return null
      }
      let text = ''
      for (const groupId in activatedGroups) {
        text = text + activatedGroups[groupId].name + ' '
      }
      return text
    }
  },
  methods: {
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
    },
    resetActivatedData () {
      this.$store.dispatch('deactivateGroup')
    },
    loadActivatedGroup () {
      this.$store.dispatch('loadActivatedGroup')
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
