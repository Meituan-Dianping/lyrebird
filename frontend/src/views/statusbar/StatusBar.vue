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
            <b >Mock group: {{activatedGroupName}}</b>
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
              <div v-else-if="item.type=='InputMenuItem'">
                <span class="input-menu-title">{{item.title+":"}}</span>
                <v-text-field
                 hide-details="false" 
                 class="input-menu-box" 
                 :value = "item.default_value"
                 @change="sendInputMsg(item, $event)"
                ></v-text-field>
              </div>
              <div v-else class="text-menu-item">{{item.src}}</div>
          </div>
        </div>
      </Poptip>
    </span>

    <span class="main-footer-status-no-pointer" v-show="processState">
      <b class="main-footer-status-button">
        <v-progress-circular
          v-if="isShowProcessing"
          size="16"
          color="white"
          width="2"
          indeterminate
        />
        <v-icon v-else-if="isShowFinish" small color="white">
          mdi-check-all
        </v-icon>
        {{processMessage}}
      </b>
    </span>


  </span>
</template>

<script>
import { makeRequest } from '@/api'

export default {
  data () {
    return {
      processMessage: '',
      processState: '',
      isShowProcessing: false,
      isShowFinish: false
    }
  },
  created () {
    this.$io.on('activatedGroupUpdate', this.loadActivatedGroup)
    this.$io.on('statusBarProcess', this.updateDatamanagerProcess)
  },
  beforeDestroy () {
    this.$io.removeListener('activatedGroupUpdate', this.loadActivatedGroup)
    this.$io.removeListener('statusBarProcess', this.updateDatamanagerProcess)
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
    updateDatamanagerProcess (payload) {
      this.processMessage = payload.message
      this.processState = payload.state
      if (this.processState === 'process') {
        this.isShowProcessing = true
        this.isShowFinish = false
      } else if (this.processState === 'finish') {
        this.isShowProcessing = false
        this.isShowFinish = true
        setTimeout(() => {
          this.isShowFinish = false
          this.processMessage = ''
          this.processState = ''
        }, 5 * 1000)
      } else {
        this.isShowProcessing = false
        this.isShowFinish = false
      }
    },
    sendInputMsg(obj, msg){
      makeRequest(obj.src, 'POST', msg)
        .then(response => {
          this.$bus.$emit('msg.success', `${obj.title}:${msg == '' ? '空' : msg} 操作成功`)
        })
        .catch(error => {
          this.$bus.$emit('msg.error', `${obj.title}:${msg == '' ? '空' : msg} 操作失败`)
        })
    }
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

.input-menu-title {
  font-size: 14px;
  margin-top: 2px;
}

.input-menu-box {
  padding: 0px;
  margin-top: 0px;
  border-bottom: 0.5px solid black;
}
</style>
