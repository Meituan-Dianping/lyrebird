<template>
  <div class="root-window">
    <div class="flow-inspector-split">
      <Split v-model="split">
        <div slot="left">
          <FlowList class="flow-inspector-left" @click.native="getfocusedFlow"></FlowList>
        </div>
        <div slot="right">
          <FlowDetail class="flow-inspector-right"></FlowDetail>
        </div>
      </Split>
    </div>
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
    listSpan () {
      if (this.focusedFlow) {
        return '12'
      } else {
        return '24'
      }
    },
    focusedFlow () {
      return this.$store.state.inspector.focusedFlow
    },
  },
  methods: {
    getfocusedFlow () {
      if (this.focusedFlow) {
        this.split = 0.5
        return true
      } else {
        this.split = 1
        return false
      }
    },
  },
}
</script>

<style scoped>
.flow-inspector-left {
  margin-right: 0px;
}
.flow-inspector-right {
  margin-left: 5px;
}
.flow-inspector-split {
  height: calc(100vh - 138px);
  border: 1px solid #dcdee2;
}
</style>
