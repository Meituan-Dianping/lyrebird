<template>
  <div>
    <ButtonBar/>

    <Row>
      <v-overlay
        :absolute="true"
        opacity="0.8"
        color="#ffffff"
        :value="spinShow"
        z-index=3
      >
        <v-progress-circular
          size="30"
          color="primary"
          width="2"
          indeterminate
        />
      </v-overlay>
      <DocumentTree :treeData="treeData" class="overflow-auto data-list" :searchStr="searchStr"/>
    </Row>

    <NodeMenu/>
    <DeleteDialog/>
    <CreateDialog/>
    <DuplicateDialog/>
  </div>
</template>

<script>
import ButtonBar from '@/views/datamanager/DataListButtonBar.vue'
import DocumentTree from '@/components/DocumentTree.vue'
import NodeMenu from '@/components/DocumentTreeNodeMenu.vue'
import DeleteDialog from '@/components/DocumentTreeDialogDelete.vue'
import CreateDialog from '@/components/DocumentTreeDialogCreate.vue'
import DuplicateDialog from '@/components/DocumentTreeDialogDuplicate.vue'
import { searchGroupByName } from '@/api'

export default {
  components: {
    ButtonBar,
    DocumentTree,
    NodeMenu,
    CreateDialog,
    DuplicateDialog,
    DeleteDialog,
  },
  computed: {
    treeData () {
      return this.$store.state.dataManager.treeData
    },
    spinShow () {
      return this.$store.state.dataManager.isLoading
    },
    searchStr () {
      return this.$store.state.dataManager.treeSearchStr
    }
  },
  watch: {
    treeData (val) {
      // Why does treeDate have Watchers, while treeData is computed property?
      // When Vue is still on mounting, value of "computed properties" is an observer, not an actual data
      if (val.length && this.$store.state.snapshot.importGroupId) {
        this.setDisplayDataDeteil()
      }
    }
  },
  methods: {
    showNode (payload) {
      this.resetGroupListOpenNode(payload)
      this.resetFocusNodeInfo(payload)
      this.resetGroupDetail(payload)
    },
    resetGroupListOpenNode (payload) {
      for (const openId of this.$store.state.dataManager.groupListOpenNode) {
        this.$store.commit('deleteGroupListOpenNode', openId)
      }
      for (const parent of payload.abs_parent_obj) {
        this.$store.commit('addGroupListOpenNode', parent.id)
      }
    },
    resetFocusNodeInfo (payload) {
      this.$store.commit('setFocusNodeInfo', payload)
    },
    resetGroupDetail (payload) {
      if (payload.type === 'group') {
        this.$store.dispatch('loadGroupDetail', payload)
      } else if (payload.type === 'data') {
        this.$store.dispatch('loadDataDetail', payload)
      } else { }
    },
    setDisplayDataDeteil () {
      const importGroupId = this.$store.state.snapshot.importGroupId
      searchGroupByName(importGroupId)
        .then(response => {
          const searchResults = response.data.data
          if (searchResults.length < 1) {
            this.$bus.$emit('msg.error', 'Load snapshot ' + importGroupId + ' error: Group id not found!')
            return
          }
          // Not handle situation of more than one groups have the same uuid
          // Only the first or searchResults is used
          const importGroup = searchResults[0]
          this.showNode(importGroup)
          this.$store.commit('clearImportGroupId')
          this.$bus.$emit('msg.success', 'Load snapshot ' + importGroup.name + ' success! ')
        }).catch(error => {
          this.$bus.$emit('msg.error', 'Load snapshot ' + importGroupId + ' error: ' + error.data.message)
        })
    }
  }
}
</script>

<style>
.data-list {
  height: calc(100vh - 44px - 40px - 30px - 1px - 12px - 28px);
  /* total:100vh
    header: 44px
    title: 40px
    button-bar: 30px
    border: 1px
    tree
    margin-bottom: 12px
    footer: 28px
  */
}
</style>
