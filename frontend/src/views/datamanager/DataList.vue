<template>
  <div>
    <Row class="button-bar">
      <Col span="23">
        <b style="padding-left:5px">Mock Data Tree</b>
      </Col>
      <Col span="1">
        <Dropdown v-show="false">
          <a href="javascript:void(0)">
            <Icon type="ios-more-outline" />
          </a>
          <DropdownMenu slot="list">
            <DropdownItem>Import...</DropdownItem>
            <DropdownItem>Export...</DropdownItem>
            <DropdownItem>Reload</DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </Col>
    </Row>
    <DocumentTree :treeData="treeData" class="data-list" />
  </div>
</template>

<script>
import DocumentTree from '@/components/DocumentTree.vue'
export default {
  components: {
    DocumentTree
  },
  computed: {
    treeData () {
      return this.$store.state.dataManager.groupList
    }
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
.button-bar-btn img {
  width: 18px;
}
</style>
