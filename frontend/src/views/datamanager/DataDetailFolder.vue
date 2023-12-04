<template>
  <div class="small-tab">
    <v-tabs
      v-model="currentTab"
      center-active
      active-class="flow-detail-active-tab"
      background-color="shading"
      color="accent"
      height="29"
      show-arrows="never"
      slider-color="primary"
    >
      <v-tab append class="flow-detail-tab" v-for="(tab, index) in tabItems" :href="'#'+tab.id" :key="index">
        {{ tab.label }}
      </v-tab>

      <v-tab-item value="info">
        <div class="data-detail">
          <div class="data-detail-content">
            <div v-for="key in groupInfoStickyTop" :key="key">
              <DataDetailInfo
                :infoKey="key"
                :editable="!uneditableKey.includes(key)"
                :deletable="!undeletableKey.includes(key)"
              />
            </div>
            <div v-for="key in groupInfoNormal" :key="key">
              <DataDetailInfo
                :infoKey="key"
                :editable="!uneditableKey.includes(key)"
                :deletable="!undeletableKey.includes(key)"
              />
            </div>
            <Row>
              <Col span="4" offset="0" align="right" style="padding:0px 10px">
                <Input v-model="newPropKey" placeholder="Input new property" size="small" />
              </Col>
              <Col span="20" style="padding:0px 0px 0px 10px">
                <Input
                  size="small"
                  v-model="newPropValue"
                  :disabled="!newPropKey"
                  :placeholder="newPropKey?'Input value':'Input KEY first to enable value input'"
                />
              </Col>
            </Row>
          </div>
        </div>
      </v-tab-item>

      <v-tab-item value="conflict">
        <div class="data-detail">
          <Row type="flex" justify="end" style="padding-top:10px">
            <Col span="18" style="padding:0px 5px 0px 10px">
              <p v-if="conflictInfo">
                Group
                <b>{{conflictCheckNode.name}}</b>
                has {{conflictInfo.length}} conflicts
              </p>
            </Col>
            <Col span="6" align="right" style="padding:0px 5px 0px 5px">
              <Button
                type="primary"
                size="small"
                :loading="isLoadConflictInfo"
                @click="getConflictInfo"
                style="margin-right:5px"
              >
                <span>{{isLoadConflictInfo ? 'Loading' : 'Start check'}}</span>
              </Button>
              <Button size="small" :disabled="isLoadConflictInfo" @click="deleteConflictInfo">
                <span>Clear</span>
              </Button>
            </Col>
          </Row>
          <DataDetailConflict :information="conflictInfo" />
        </div>
      </v-tab-item>

      <v-tab-item v-for="(tab, index) in customTabInfo" :value="tab.id" :key="index">
        <div class="data-detail">
          <div class="data-detail-content">
            <div v-for="(value, key) in tab.content" :key="key">
              <DataDetailInfo
                :infoKey="key"
                :editable="!uneditableKey.includes(key)"
                :deletable="!undeletableKey.includes(key)"
              />
            </div>
          </div>
        </div>
      </v-tab-item>
    </v-tabs>

    <div class="save-btn" v-show="groupInfo">
      <v-tooltip top v-if="currentTab === 'info'">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            v-bind="attrs"
            v-on="on"
            fab
            dark
            color="primary"
            class="save-btn-detail"
            @click="saveGroupDetail"
          >
            <v-icon
            class="save-btn-icon"
            dark>
              mdi-content-save-outline
            </v-icon>
          </v-btn>
        </template>
        <span>Save (⌘+s)</span>
      </v-tooltip>

      <v-tooltip top v-else-if="currentTab !== 'conflict'">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            v-bind="attrs"
            v-on="on"
            fab
            dark
            color="primary"
            class="save-btn-detail"
            @click="sendCustomTagInfo"
          >
            <v-icon
            class="save-btn-icon"
            dark>
              mdi-send
            </v-icon>
          </v-btn>
        </template>
        <span>Send</span>
      </v-tooltip>
    </div>
  </div>
</template>

<script>
import DataDetailConflict from '@/views/datamanager/DataDetailConflict.vue'
import DataDetailInfo from "@/views/datamanager/DataDetailInfo.vue"

export default {
  components: {
    DataDetailConflict,
    DataDetailInfo,
  },
  data () {
    return {
      currentTab: "information",
      conflictCheckNode: {},
      newPropKey: '',
      newPropValue: ''
    }
  },
  mounted () {
    this.$bus.$on('keydown', this.onKeyDown)
  },
  beforeDestroy () {
    this.$bus.$off('keydown', this.onKeyDown)
  },
  activated () {
    this.$bus.$on('keydown', this.onKeyDown)
  },
  deactivated () {
    this.$bus.$off('keydown', this.onKeyDown)
  },
  computed: {
    nodeInfo () {
      return this.$store.state.dataManager.focusNodeInfo
    },
    groupInfo () {
      return this.$store.state.dataManager.groupDetail
    },
    tabItems () {
      let tabs = [
        {id: 'info', label: 'Information'},
        {id: 'conflict', label: 'Conflict'}
      ]
      for (const customTab of this.customTabInfo) {
        tabs.push({
          id: customTab.id,
          label: customTab.id
        })
      }
      return tabs
    },
    customTabInfo () {
      let info = {}
      for (const key in this.groupInfo) {
        const value = this.groupInfo[key]
        if (typeof(value) === 'object' && value.hasOwnProperty('tab')) {
          if (!info.hasOwnProperty(value.tab)) {
            info[value.tab] = {}
          }
          info[value.tab][key] = value
        }
      }
      let arr = []
      for (const key in info) {
        arr.push({
          id: key,
          content: info[key]
        })
      }
      return arr
    },
    groupInfoStickyTop () {
      let keys = []
      for (const key of this.stickyTopKey) {
        if (this.groupInfo.hasOwnProperty(key)) {
          keys.push(key)
        }
      }
      return keys
    },
    groupInfoNormal () {
      let keys = []
      for (const key in this.groupInfo) {
        if (
          !this.stickyTopKey.includes(key) && 
          !this.undisplayedKey.includes(key) && 
          key.substring(0, 1) !== '_' &&
          !this.groupInfo[key].hasOwnProperty('tab')
        ) {
          keys.push(key)
        }
      }
      return keys
    },
    conflictInfo () {
      return this.$store.state.dataManager.conflictInfo
    },
    isLoadConflictInfo () {
      return this.$store.state.dataManager.isLoadConflictInfo
    },
    undisplayedKey () {
      return this.$store.state.dataManager.undisplayedKey
    },
    undeletableKey () {
      return this.$store.state.dataManager.undeletableKey
    },
    uneditableKey () {
      return this.$store.state.dataManager.uneditableKey
    },
    stickyTopKey () {
      return this.$store.state.dataManager.stickyTopKey
    },
  },
  methods: {
    saveGroupDetail () {
      if (this.newPropKey) {
        if (this.newPropKey.match(/^[ ]+$/)) {
          this.$bus.$emit('msg.error', 'Group property key illegal: ' + 'All space')
        } else if (this.undisplayedKey.includes(this.newPropKey)) {
          this.$bus.$emit('msg.error', 'Group property key illegal: Keyword ' + this.newPropKey + ' is not allowed!')
        } else if (this.$store.state.dataManager.groupDetail.hasOwnProperty(this.newPropKey)) {
          this.$bus.$emit('msg.error', 'Group property key illegal: Property ' + this.newPropKey + ' exists!')
        } else {
          this.$store.commit('setGroupDetailItem', { key: this.newPropKey, value: this.newPropValue })
          this.$store.dispatch('saveGroupDetail', this.groupInfo)
          this.newPropKey = ''
          this.newPropValue = ''
        }
      } else {
        this.$store.dispatch('saveGroupDetail', this.groupInfo)
      }
    },
    sendCustomTagInfo () {
      this.$store.dispatch('sendGroupDetail', {
        tab: this.currentTab
      })
    },
    getConflictInfo () {
      this.conflictCheckNode = this.nodeInfo
      this.$store.commit('setIsLoadConflictInfo', true)
      this.$store.commit('clearConflictInfo')
      this.$store.dispatch('loadConflict', this.nodeInfo)
    },
    deleteConflictInfo () {
      this.$store.commit('clearConflictInfo')
    },
    onKeyDown (event) {
      if (event.code !== "KeyS" || !event.metaKey) {
        return
      }
      this.saveGroupDetail()
      event.preventDefault()
      console.log("Save", event)
    }
  }
}
</script>

<style>
.data-detail {
  height: calc(100vh - 44px - 40px - 28px - 33px - 28px - 12px);
  /* total:100vh
  header: 44px
  title: 40px
  breadcrumb: 28px
  buttonBar: 33px
  codeEditor
  margin-botton:12px
  footer: 28px
    */
  font-size: 14px;
}
.data-detail-content {
  margin: 10px 5px 10px 10px;
  height: calc(100vh - 44px - 40px - 30px - 1px - 33px - 10px - 10px - 10px - 28px);
  /* total:100vh
    header: 44px
    title: 40px
    button-bar: 30px
    border: 1px
    tab: 33px
    margin-bottom: 10px
    detail
    margin-bottom: 10px
    footer: 28px
  */
  overflow-y: scroll;
}
</style>
