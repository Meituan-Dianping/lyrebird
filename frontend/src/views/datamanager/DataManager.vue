<template>
  <Split v-model="split" class="datamanager-split">
    <div slot="left">
      <data-list></data-list>
    </div>
    <div slot="right">
      <data-detail></data-detail> 
    </div>
  </Split>
</template>

<script>
import DataList from '@/views/datamanager/DataList.vue'
import DataDetail from '@/views/datamanager/DataDetail.vue'
export default {
  components: {
    DataList,
    DataDetail
  },
  mounted() {
    this.$store.dispatch('loadDataMap')
  },
  data() {
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
</style>
