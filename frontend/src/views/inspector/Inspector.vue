<template>
  <div class="small-tab">
    <Row class="inspector-container-button-bar">
      <button-bar></button-bar>
    </Row>
    <div class="divider"></div>
    <Tabs :value="selectedModeTab" size="small" @on-click="switchTab">
      <TabPane label="Real-time" name="realtime"></TabPane>
      <TabPane label="Advanced" name="advanced"></TabPane>
    </Tabs>
    <FlowInspector v-if="selectedModeTab==='realtime'"></FlowInspector>
    <EventInspector v-if="selectedModeTab==='advanced'"></EventInspector>
  </div>
</template>

<script>
import ButtonBar from '@/views/inspector/ButtonBar.vue'
import EventInspector from '@/views/event/EventInspector.vue'
import FlowInspector from '@/views/inspector/FlowInspector.vue'

export default {
  name: 'Inspector',
  data () {
    return {
      activatedData: null,
      selectedDataGroup: '',
      selectedModeTab: 'realtime'
    }
  },
  components: {
    ButtonBar,
    EventInspector,
    FlowInspector
  },
  mounted() {
    this.$store.dispatch('loadActivatedGroup')
  },
  methods: {
    switchTab (name) {
      this.selectedModeTab = name
    }
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
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
</style>
