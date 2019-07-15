<template>
  <div>
    <Row class="button-bar">
      <Col span="12">
        <span v-for="(value, index) in nodeParents" :key="value.id">
          {{value.name}}
          {{index === nodeParents.length-1 ? '' : ' - '}}
        </span>
      </Col>
      <Col span="12" align="right">
        <JsonPathBar class="json-path-bar"></JsonPathBar>
      </Col>
    </Row>
    <component v-if="nodeInfo.type" :is="getComponentByType(nodeInfo)" />
    <div v-else class="data-detail-empty">
      No selected data
    </div>
  </div>
</template>

<script>
import DataDetailRequest from '@/views/datamanager/DataDetailRequest.vue'
import DataDetailFolder from '@/views/datamanager/DataDetailFolder.vue'
import JsonPathBar from '@/views/datamanager/JsonPathBar.vue'
import Icon from 'vue-svg-icon/Icon.vue'

export default {
  components: {
    DataDetailRequest,
    DataDetailFolder,
    JsonPathBar,
    Icon
  },
  computed: {
    dataDetail() {
      return this.$store.state.dataManager.dataDetail
    },
    nodeInfo() {
      return this.$store.state.dataManager.focusNodeInfo
    },
    nodeParents() {
      if (this.nodeInfo && this.nodeInfo.id) {
        let parents = []
        let tree = this.nodeInfo
        while(tree.id) {
          parents.push({
            id: tree.id,
            name: tree.name
          })
          tree = tree.parent
        }
        return parents.reverse()
      } else {
        return []
      }
    }
  },
  methods: {
    getComponentByType(payload) {
      if (payload.type === 'data') {
        return 'DataDetailRequest'
      } else if (payload.type === 'group') {
        return 'DataDetailFolder'
      } else {
        return ''
      }
    }
  }
}
</script>

<style scoped>
.button-bar {
  height: 27px;
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ddd;
  background-color: #f8f8f9;
}
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
.save-btn {
  color: #fff;
  font-size: 0.6rem;
  text-align: center;
  line-height: 3rem;
  width: 3rem;
  height: 3rem;
  position: fixed;
  right: 50px;
  bottom: 70px;
  border-radius: 50%;
  z-index: 500;
}
.save-btn > .ivu-tooltip > .ivu-tooltip-rel > .ivu-btn {
  padding: 5px 8px 5px;
  background-color: #0fccbf;
  border-color: #0fccbf;
}
.data-detail-empty {
  position: absolute; 
  top:40%;
  left:50%;
  transform:translate(-50%,-50%);
  text-align: center;
}
</style>
