<template>
  <div class="checker-split">
    <Split v-model="split" min=220px>
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
  height: calc(100vh - 44px - 40px - 28px - 12px);
}
.extension-empty {
  position: absolute; 
  top:50%;
  left:50%;
  transform:translate(-50%,-50%);
  text-align: center;
}
.empty-icon {
  height: 72px !important;
  width: 72px !important;
  font-size: 72px !important;
  margin-bottom: 16px;
}
.empty-text {
  font-weight: 400;
  font-family: PingFangSC-Regular;
  font-size: 14px;
  color: #000520;
  line-height: 14px;
  margin-bottom: 0px !important;
}
</style>
