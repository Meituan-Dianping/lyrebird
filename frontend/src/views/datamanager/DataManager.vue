<template>
  <div class="snapshot-import-spin">
    <snapshot-import-spin></snapshot-import-spin>
    <snapshot-import-selector></snapshot-import-selector>
    <Split v-model="split" class="datamanager-split">
      <div slot="left">
        <data-list></data-list>
      </div>
      <div slot="right">
        <data-detail></data-detail>
      </div>
    </Split>
  </div>
</template>

<script>
import DataList from '@/views/datamanager/DataList.vue'
import DataDetail from '@/views/datamanager/DataDetail.vue'
import SnapshotImportSelector from '@/views/datamanager/SnapshotImportSelector.vue'
import SnapshotImportSpin from '@/views/datamanager/SnapshotImportSpin.vue'

export default {
  components: {
    DataList,
    DataDetail,
    SnapshotImportSelector,
    SnapshotImportSpin
  },
  mounted() {
    this.$store.dispatch('loadDataMap')
  },
  computed: {
    spinDisplay (){
      return this.$store.state.dataManager.spinDisplay
    }
},
  data () {
    return {
      split: 0.35
    }
  }
}
</script>

<style scoped>
.datamanager-split{
  height: calc(100vh - 66px);
  /* total:100vh
    header: 38px
    tree
    footer: 28px
  */
  border: 1px solid #dcdee2;
}
.snapshot-import-spin{
  height: 100%;
  position: relative;
}
</style>
