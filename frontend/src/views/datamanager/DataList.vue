<template>
  <div>
    <Row class="button-bar">
      <Col span="12">
        <Tooltip content="Add folder" placement="bottom-start" :delay="500">
          <Icon class="button-bar-button" type="md-folder" size="16" color="#666" />
        </Tooltip>
        <Tooltip content="Add file" placement="bottom-start" :delay="500">
          <Icon class="button-bar-button" type="md-document" size="16" color="#666" />
        </Tooltip>
      </Col>
      <Col span="12" align="right">
        <Tooltip content="Synchronize" placement="bottom" :delay="500">
          <Icon class="button-bar-button-right" type="md-sync" size="16" color="#666" />
        </Tooltip>
      </Col>
    </Row>
    <DocumentTree :treeData="treeData" class="data-list"/>
  </div>
</template>

<script>
import DocumentTree from '@/components/DocumentTree.vue'
export default {
  components: {
    DocumentTree
  },
  created() {
    this.$bus.$on('treeChange', this.setTreeData)
  },
  computed: {
    treeData() {
      return this.$store.state.dataManager.groupList
    }
  },
  methods: {
    setTreeData(payload) {
      console.log('Moved:', payload.name, ', id:', payload.id)
      let tree = payload
      let parentsStr = ''
      while (tree.parent.name) {
        parentsStr += tree.parent.name
        parentsStr += ' '
        tree = tree.parent
      }
      console.log('New parents:', parentsStr)
      console.log('Whole tree data', this.treeData)
      // this.$store.commit('setDataList', payload)
    },
    // setSelectedTreeNode(payload) {
    //   console.log('selected node:', payload.name, ', id:', payload.id)
    // }
  }
}
</script>

<style scoped>
.data-list {
  height: calc(100vh - 94px);
  /* total:100vh
    header: 38px
    buttonBar: 28px
    tree
    footer: 28px
  */
  overflow-y: auto;
  margin-right: 0;
}
.button-bar {
  height: 27px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #ddd;
  background-color: #f8f8f9;
}
.button-bar-button {
  padding: 5px 10px 5px 0px;
  cursor: pointer;
}
.button-bar-button-right {
  padding: 5px 0px 5px 10px;
  cursor: pointer;
}
</style>
