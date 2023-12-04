<template>
  <v-navigation-drawer
    class="inspector-drawer"
    v-model="shown"
    absolute
    temporary
    hide-overlay
    right
    width="600"
    color="rgba(230, 230, 230, 0.8)"
  >

    <DataListButtonBar :editable="false"/>

    <TempMockTree :searchStr="searchStr"/>

    <DocumentTree :treeData="treeData" class="overflow-auto data-list" :searchStr="searchStr" :editable="false" :deletable="false"/>

  </v-navigation-drawer>
</template>
  
<script>
import TempMockTree from '@/views/inspector/TempMockTree.vue'
import DocumentTree from '@/components/DocumentTree.vue'
import DataListButtonBar from '@/views/datamanager/DataListButtonBar.vue'

export default {
  components: {
    TempMockTree,
    DocumentTree,
    DataListButtonBar
  },
  activated () {
    this.$store.dispatch('loadTempMockData')
  },
  data() {
    return {
      shown: false
    }
  },
  computed: {
    treeData () {
      return this.$store.state.dataManager.groupList
    },
    temporaryMockDataList () {
      return this.$store.state.dataManager.temporaryMockDataList
    },
    searchStr () {
      return this.$store.state.dataManager.treeSearchStr
    }
  },
  methods: {
    toggal () {
      this.shown = !this.shown
    }
  }
}
</script>
  
<style>
.inspector-drawer {
  z-index: 4;
}
.data-list-button-bar-search .v-input__prepend-inner {
  margin-top: -2px !important;
}
.data-list-button-bar-search .v-input__slot {
  padding: 0px 4px !important;
  min-height: 20px !important;
  height: 20px !important;
}
.data-list-button-bar-search .v-icon.v-icon {
  font-size: 12px;
}
.data-list-button-bar-search .v-text-field input {
  font-size: 12px;
  padding: 0px !important;
}
</style>
  