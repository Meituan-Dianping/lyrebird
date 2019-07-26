<template>
  <div>
    <DraggableTree :data="treeData" :draggable=false cross-tree="cross-tree" :space=0 @change="onTreeChange">
      <div slot-scope="{data, store}">
        <template v-if="!data.isDragPlaceHolder">
          <DocumentTreeNode :data="data" :treestore="store"/>
        </template>
      </div>
    </DraggableTree>
  </div>
</template>

<script>
import { DraggableTree } from 'vue-draggable-nested-tree'
import DocumentTreeNode from '@/components/DocumentTreeNode.vue'

export default {
  components: {
    DraggableTree,
    DocumentTreeNode
  },
  props: ['treeData'],
  methods: {
    onTreeChange(payload) {
      this.$bus.$emit('treeChange', payload)
    }
  }
}
</script>

<style>
.he-tree {
  /* 整个组件 */
  padding: 5px;
}
.tree-node {
  /* 整个树 */
}
.tree-node-inner-back {
  /* 树结点 */
  margin-bottom: 0px
}
.tree-node-inner {
  /* 树结点 */
  padding: 0px;
}
.draggable-placeholder {
  /* 拖拽时的槽 */
}
.draggable-placeholder-inner {
  /* 被拖拽对象 */
  border: 1px dashed #0088f8;
  box-sizing: border-box;
  background: rgba(0, 136, 249, 0.09);
  color: #0088f9;
  text-align: center;
  padding: 0;
  display: flex;
  align-items: center;
}
</style>
