<template>
  <div>
    <Row class="button-bar">
      <Col span="15" class="button-bar-line">
        <span v-for="(value, index) in nodeParents" :key="value.id">
          <Icon v-if="value.isRoot" type="ios-home" @click="showNode(value)" style="cursor: pointer;"/>
          <a v-else @click="showNode(value)">{{value.name}}</a>
          {{index === nodeParents.length-1 ? '' : ' > '}}
        </span>
      </Col>
      <Col span="8" offset="1" align="right" class="button-bar-line">
        <JsonPathBar/>
      </Col>
    </Row>
    <component v-if="nodeInfo.type" :is="getComponentByType(nodeInfo)" />
    <div v-else class="data-detail-empty">No selected data</div>
  </div>
</template>

<script>
import DataDetailHttpData from '@/views/datamanager/DataDetailHttpData.vue'
import DataDetailFolder from '@/views/datamanager/DataDetailFolder.vue'
import JsonPathBar from '@/views/datamanager/JsonPathBar.vue'

export default {
  components: {
    DataDetailHttpData,
    DataDetailFolder,
    JsonPathBar
  },
  computed: {
    dataDetail () {
      return this.$store.state.dataManager.dataDetail
    },
    nodeInfo () {
      return this.$store.state.dataManager.focusNodeInfo
    },
    nodeParents () {
      if (this.nodeInfo && this.nodeInfo.id) {
        let parents = []
        let tree = this.nodeInfo
        while (tree.id) {
          parents.push({
            id: tree.id,
            name: tree.name,
            type: tree.type,
            isRoot: tree.parent_id ? false: true
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
    getComponentByType (payload) {
      if (payload.type === 'data') {
        return 'DataDetailHttpData'
      } else if (payload.type === 'group') {
        return 'DataDetailFolder'
      } else {
        return ''
      }
    },
    showNode (payload) {
      this.resetFocusNodeInfo(payload)
      this.resetGroupDetail(payload)
    },
    resetFocusNodeInfo (payload) {
      this.$store.commit('setFocusNodeInfoByGroupInfo', payload)
    },
    resetGroupDetail (payload) {
      if (payload.type === 'group') {
        this.$store.dispatch('loadGroupDetail', payload)
      } else if (payload.type === 'data') {
        this.$store.dispatch('loadDataDetail', payload)
      } else { }
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
}
.button-bar-line {
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
.data-detail-empty {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
</style>
