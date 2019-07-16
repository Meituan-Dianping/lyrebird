<template>
  <div>
    <Row class="inspector-container-button-bar">
      <button-bar></button-bar>
    </Row>
    <div class="divider"></div>
    <Row>
      <Col :span="listSpan">
        <flow-list class="inspector-left"></flow-list>
      </Col>
      <div class="split" v-if="focusedFlow"></div>
      <Col span="12" v-if="focusedFlow">
        <flow-detail class="inspector-right"></flow-detail>
      </Col>
    </Row>
  </div>
</template>

<script>
let stopedStatus = {
  recording: false,
  type: 'record',
  color: 'red',
  text: 'Start recording'
};
let recordingStatus = {
  recording: true,
  type: 'stop',
  color: 'black',
  text: 'Stop recording'
};
import FlowList from '@/views/inspector/FlowList.vue'
import FlowDetail from '@/views/inspector/FlowDetail.vue'
import ButtonBar from '@/views/inspector/ButtonBar.vue'

export default {
  name: 'Inspector',
  data: function () {
    return {
      activatedData: null,
      selectedDataGroup: '',
    };
  },
  components: {
    FlowList,
    FlowDetail,
    ButtonBar,
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
.inspector-container-button-bar {
  height: 38px;
  display: flex;
  align-items: center;
}
.inspector-left {
  margin-right: 0px;
}
.inspector-right {
  margin-left: 5px;
}
.divider {
  display: block;
  width: 100%;
  height: 1px;
  background: #eee;
  top: 0;
  left: 0;
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
