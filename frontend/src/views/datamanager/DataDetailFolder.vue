<template>
  <div class="small-tab">
    <tabs v-model="currentTab" :animated="false" size="small">
      <tab-pane label="Information" name="information">
        <DataDetailInfo class="data-detail" :information="groupInfo"/>
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
      isLoadConflictInfo: false,
      conflictCheckNode: {}
    }
  },
  computed: {
    nodeInfo() {
      return this.$store.state.dataManager.focusNodeInfo
    },
    groupInfo() {
      return this.$store.state.dataManager.groupDetail
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
      this.conflictCheckNode = this.nodeInfo
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
