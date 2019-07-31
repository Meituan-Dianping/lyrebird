<template>
  <div class="small-tab">
    <tabs v-model="currentTab" :animated="false" size="small">
      <tab-pane label="Information" name="information">
        <div class="data-detail">
          <Row style="padding-top:10px">
            <Col span="18" style="padding:0px 5px 0px 10px">
              <Icon type="md-information-circle" />
              Information of Group <b>{{groupInfo.id}}</b>
            </Col>
            <Col span="6" align="right">
              <Button type="primary" size="small" :disabled="!isGroupDetailChanged" @click="saveGroupDetail" style="margin-right:5px">
                <span>Save</span>
              </Button>
              <Button size="small" :disabled="!isGroupDetailChanged" @click="loadGroupDetail" style="margin-right:5px">
                <span>Cancel</span>
              </Button>
            </Col>
          </Row>
          <div style="margin:10px 5px 0px 10px">
            <div v-for="(value, key) in groupInfo" :key="key">
              <DataDetailInfo v-if="undisplayedInfoKey.indexOf(key) === -1 && key.substring(0,1) !== '_'" :infoValue="value" :infoKey="key"/>
            </div>
            <Row style="padding-top:10px">
              <Col span="5" offset="1" align="right" style="padding:0px 10px 0px 10px">
                <Input v-model="newPropKey" placeholder="Input new property" size="small"/>
              </Col>
              <Col span="18" style="padding:0px 0px 0px 10px">
                <Input v-model="newPropValue" :disabled="!newPropKey" :placeholder="newPropKey?'Input value':'Input KEY first to enable value input'" size="small"/>
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
                <Icon type="md-information-circle" />
                Group <b>{{conflictCheckNode.name}}</b> has {{conflictInfo.length}} conflicts
              </p>
            </Col>
            <Col span="6" align="right" style="padding:0px 5px 0px 5px">
              <Button type="primary" size="small" :loading="isLoadConflictInfo" @click="getConflictInfo" style="margin-right:5px">
                <span v-if="isLoadConflictInfo">Loading</span>
                <span v-else>Start check</span>
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
  </div>
</template>

<script>
import DataDetailConflict from '@/views/datamanager/DataDetailConflict.vue'
import DataDetailInfo from "@/views/datamanager/DataDetailInfo.vue"

export default {
  components: {
    DataDetailConflict,
    DataDetailInfo
  },
  data() {
    return {
      currentTab: "information",
      undisplayedInfoKey: ['children', 'type', 'parent_id'],
      isLoadConflictInfo: false,
      conflictCheckNode: {},
      newPropKey: '',
      newPropValue: ''
    }
  },
  computed: {
    nodeInfo() {
      return this.$store.state.dataManager.focusNodeInfo
    },
    groupInfo() {
      return this.$store.state.dataManager.groupDetail
    },
    isGroupDetailChanged() {
      return this.$store.state.dataManager.isGroupDetailChanged
    },
    conflictInfo() {
      if (this.$store.state.dataManager.conflictInfo) {
        this.isLoadConflictInfo = false
      }
      return this.$store.state.dataManager.conflictInfo
    }
  },
  watch: {
    newPropKey () {
      if (this.newPropKey) {
        this.$store.commit('setIsGroupDetailChanged', true)
      } else {
        this.$store.commit('setIsGroupDetailChanged', false)
      }
    }
  },
  methods: {
    saveGroupDetail() {
      if (this.newPropKey) {
        if (this.newPropKey.match(/^[ ]+$/)) {
          this.$bus.$emit('msg.error', 'Group property key illegal: ' + 'All space')
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
      this.$store.commit('setIsGroupDetailChanged', false)
    },
    getConflictInfo() {
      this.conflictCheckNode = this.nodeInfo
      this.isLoadConflictInfo = true
      this.$store.commit('clearConflictInfo')
      this.$store.dispatch('loadConflict', this.nodeInfo)
    },
    deleteConflictInfo() {
      this.$store.commit('clearConflictInfo')
    },
    loadGroupDetail() {
      this.$store.dispatch('loadGroupDetail', this.groupInfo)
      this.newPropKey = ''
      this.newPropValue = ''
      this.$store.commit('setIsGroupDetailChanged', false)
    }
  }
}
</script>

<style>
.data-detail {
  height: calc(100vh - 127px);
  /* total:100vh
  header: 38px
  buttonBar: 24px
  tab-header: 34px
  buttonBar: 34px
  padding: 10px
  table
  footer: 28px
    */
  overflow-y: auto;
  font-size: 14px;
}
</style>
