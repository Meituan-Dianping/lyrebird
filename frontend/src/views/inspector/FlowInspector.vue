<template>
  <div class="inspector-realtime-split">
    <Split v-model="split" min="0px" max="0px">
      <div slot="left">
        <FlowList class="inspector-realtime-left"></FlowList>
      </div>
      <div slot="right">
        <FlowDetail v-if="focusedFlowDetail" class="inspector-realtime-right"></FlowDetail>
        <div v-else class="flow-detail-empty">No selected flow</div>
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
    focusedFlowDetail () {
      return this.$store.state.inspector.focusedFlowDetail
    },
  },
  watch: {
    focusedFlowDetail (val) {
      if (!val) {
        this.split = 1
      } else if (this.split === 1) {
        this.split = 0.5
      } else { }
    }
  }
}
</script>

<style scope>
.inspector-realtime-left {
  margin-right: 0px;
}
.inspector-realtime-right {
  margin-left: 5px;
}
.inspector-realtime-split {
  height: calc(100vh - 44px - 38px - 28px - 2px);
  /* total:100vh
  header: 44px
  buttonBar: 38px
  split
  border: 2px
  footer: 28px
    */
}
.flow-detail-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
</style>
