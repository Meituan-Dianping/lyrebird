<template>
  <div class="small-tab">
    <tabs v-model="currentTab" :animated="false" size="small">
      <tab-pane label="Information" name="information">
        <DataDetailInfo class="data-detail" :information="displayGroupInfo"/>
      </tab-pane>
      <tab-pane label="Conflict" name="conflict">
        <div class="data-detail">
          <Row style="padding-top:10px">
            <Col span="9" offset="1" >
              Result of data <b>{{nodeInfo.name}}</b>
            </Col>
            <Col span="11" align="right">
              <Button size="small" :disabled="isLoadConflictInfo" @click="deleteConflictInfo">
                <span>Clear</span>
              </Button>
            </Col>
            <Col span="3" align="right">
              <Button type="primary" size="small" :loading="isLoadConflictInfo" @click="getConflictInfo">
                <span v-if="isLoadConflictInfo">Loading...</span>
                <span v-else>Start checking</span>
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
      isLoadConflictInfo: false,
      unshowInfoKey: ['children']
    }
  },
  computed: {
    nodeInfo() {
      return this.$store.state.dataManager.focusNodeInfo
    },
    groupInfo() {
      return this.$store.state.dataManager.groupDetail
    },
    displayGroupInfo() {
      let res = {}
      for (const key in this.groupInfo) {
        if (this.unshowInfoKey.indexOf(key) === -1 && key.substring(0,1) !== '_') {
          res[key] = this.groupInfo[key]
        }
      }
      return res
    },
    conflictInfo() {
      if (this.$store.state.dataManager.conflictInfo) {
        this.isLoadConflictInfo = false
      }
      return this.$store.state.dataManager.conflictInfo
    }
  },
  methods: {
    getConflictInfo() {
      this.isLoadConflictInfo = true
      this.$store.commit('clearConflictInfo')
      this.$store.dispatch('loadConflict', this.nodeInfo)
    },
    deleteConflictInfo() {
      this.$store.commit('clearConflictInfo')
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
