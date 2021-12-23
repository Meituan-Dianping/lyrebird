<template>
  <div>
    <snapshot-import-selector></snapshot-import-selector>
    <Split v-model="split" min=300px max=543px class="datamanager-split">
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

export default {
  components: {
    DataList,
    DataDetail,
    SnapshotImportSelector,
  },
  mounted() {
    this.loadDataMap()
    this.$store.dispatch('loadActivatedGroup')
    this.$store.dispatch('loadIsLabelDisplay')
  },
  created () {
    this.$io.on('datamanagerUpdate', this.loadDataMap)
  },
  destroyed() {
    this.$io.removeListener('datamanagerUpdate', this.loadDataMap)
  },
  data () {
    return {
      split: 0.35
    }
  },
  methods: {
    loadDataMap () {
      this.$store.dispatch('loadDataMap')
    }
  }
}
</script>

<style scoped>
.datamanager-split{
  height: calc(100vh - 44px - 40px - 28px - 12px);
  /* total:100vh
    header: 44px
    title: 40px
    tree
    margin-bottom: 12px
    footer: 28px
  */
}
</style>
