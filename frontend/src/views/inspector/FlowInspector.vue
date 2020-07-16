<template>
  <div class="inspector-realtime-split">
    <Split v-model="split">
      <div slot="left">
        <FlowList class="inspector-realtime-left"></FlowList>
      </div>
      <div v-if="focusedFlow" slot="right">
        <FlowDetail class="inspector-realtime-right"></FlowDetail>
      </div>
    </Split>
  </div>
</template>

<script>
import FlowList from '@/views/inspector/FlowList.vue'
import FlowDetail from '@/views/inspector/FlowDetail.vue'

export default {
  components: {
    FlowList,
    FlowDetail
  },
  data () {
    return {
      split: 1
    }
  },
  computed: {
    focusedFlow () {
      return this.$store.state.inspector.focusedFlow
    },
  },
  watch: {
    focusedFlow (val) {
      this.split = val ? 0.5 : 1
    }
  }
}
</script>

<style scoped>
.inspector-realtime-left {
  margin-right: 0px;
}
.inspector-realtime-right {
  margin-left: 5px;
}
.inspector-realtime-split {
  height: calc(100vh - 138px); 
  /* total:100vh
  header: 38px
  buttonBar: 38px
  mode-tab 34px
  split
  footer: 28px
    */
  border: 1px solid #dcdee2;
}
</style>
