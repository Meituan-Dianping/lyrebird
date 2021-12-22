<template>
  <div class="small-tab">
    <Row class="inspector-container-button-bar">
      <button-bar></button-bar>
    </Row>
    <div class="divider"></div>

    <FlowInspector/>

  </div>
</template>

<script>
import ButtonBar from '@/views/inspector/ButtonBar.vue'
import FlowInspector from '@/views/inspector/FlowInspector.vue'

export default {
  name: 'Inspector',
  components: {
    ButtonBar,
    FlowInspector
  },
  mounted() {
    this.$store.dispatch('loadActivatedGroup')
  }
}
</script>

<style scoped>
.inspector-container-button-bar {
  height: 38px;
  display: flex;
  align-items: center;
}
.divider {
  display: block;
  width: 100%;
  height: 1px;
  background: #eee;
  top: 0;
  left: 0;
}
</style>
