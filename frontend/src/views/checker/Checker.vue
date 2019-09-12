<template>
  <div class="checker-split">
    <Split v-model="split">
      <div slot="left">
        <checker-list></checker-list>
      </div>
      <div slot="right">
        <checker-detail></checker-detail>
      </div>
    </Split>
  </div>
</template>

<script>
import CheckerList from '@/views/checker/CheckerList.vue'
import CheckerDetail from '@/views/checker/CheckerDetail.vue'

export default {
  data() {
    return {
      split: 0.2
    }
  },
  components: {
    CheckerList,
    CheckerDetail
  },
  created() {
    this.$store.dispatch('loadCheckers')
  }
}
</script>

<style>
.checker-split{
  height: calc(100vh - 66px);
  border: 1px solid #dcdee2;
}
.checker-empty {
  position: absolute; 
  top:40%;
  left:50%;
  transform:translate(-50%,-50%);
  text-align: center;
}
</style>
