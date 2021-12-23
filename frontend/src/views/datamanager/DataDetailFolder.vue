<template>
  <div class="small-tab">
    <tabs v-model="currentTab" :animated="false" size="small">
      <tab-pane label="Information" name="information">
        <div class="data-detail">
          <div class="data-detail-content">
            <div v-for="(value, key) in groupInfoStickyTop" :key="key">
              <DataDetailInfo
                :infoKey="key"
                :editable="!uneditableKey.includes(key)"
                :deletable="!undeletableKey.includes(key)"
              />
            </div>
            <div v-for="(value, key) in groupInfoNormal" :key="key">
              <DataDetailInfo
                :infoValue="value"
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
      </tab-pane>
      <tab-pane label="Conflict" name="conflict">
        <div class="data-detail">
          <Row type="flex" justify="end" style="padding-top:10px">
            <Col span="18" style="padding:0px 5px 0px 10px">
              <p v-if="conflictInfo">
                <Icon type="md-information-circle" />Group
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
      </tab-pane>
    </tabs>

    <div class="save-btn" v-if="groupInfo">
      <v-tooltip top>
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
    </div>
  </div>
</template>

<script>
import DataDetailConflict from '@/views/datamanager/DataDetailConflict.vue'
import DataDetailInfo from "@/views/datamanager/DataDetailInfo.vue"
import Icon from 'vue-svg-icon/Icon.vue'

export default {
  components: {
    DataDetailConflict,
    DataDetailInfo,
    Icon
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
  computed: {
    nodeInfo () {
      return this.$store.state.dataManager.focusNodeInfo
    },
    groupInfo () {
      return this.$store.state.dataManager.groupDetail
    },
    groupInfoStickyTop () {
      const groupInfo = this.$store.state.dataManager.groupDetail
      let stickyTopInfo = {}
      for (const key in groupInfo) {
        if (this.stickyTopKey.includes(key)) {
          stickyTopInfo[key] = groupInfo[key]
        }
      }
      return stickyTopInfo
    },
    groupInfoNormal () {
      const groupInfo = this.$store.state.dataManager.groupDetail
      let notStickyTopInfo = {}
      for (const key in groupInfo) {
        if (!this.stickyTopKey.includes(key) && !this.undisplayedKey.includes(key) && key.substring(0, 1) !== '_') {
          notStickyTopInfo[key] = groupInfo[key]
        }
      }
      return notStickyTopInfo
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
  overflow-y: auto;
  font-size: 14px;
}
.data-detail-content {
  margin:10px 5px 10px 10px;
  height:calc(100vh - 44px - 40px - 28px - 33px - 28px - 12px); 
  overflow-y:scroll
}
.save-btn {
  color: #fff;
  font-size: 0.6rem;
  text-align: center;
  line-height: 3rem;
  width: 3rem;
  height: 3rem;
  position: fixed;
  right: 60px;
  bottom: 60px;
  border-radius: 50%;
  z-index: 500;
}
.save-btn-detail {
  width: 36px !important;
  height: 36px !important;
}
.save-btn-icon {
  font-size: 20px !important;
  width: 20px !important;
  height: 20px !important;
}
</style>
