<template>
  <div>
    <Row>
      <Col :span="listSpan">
        <FlowList class="inspector-left"></FlowList>
      </Col>
      <div class="split" v-if="focusedFlow"></div>
      <Col span="12" v-if="focusedFlow">
        <FlowDetail class="inspector-right"></FlowDetail>
      </Col>
    </Row>
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
    }
  }
}
</script>

<style scoped>
.inspector-left {
  margin-right: 0px;
}
.inspector-right {
  margin-left: 5px;
}
.split {
  display: block;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  border: 1px dashed #eee;
}
</style>
