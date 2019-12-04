<template>
  <div>
    <Row type="flex" justify="center" align="middle">
      <Col span="1">
        <Button icon="ios-arrow-dropright-circle" type="text" size="small" @click="dismiss"></Button>
      </Col>
      <Col span="23" class="small-tab">
        <Tabs :value="currentTab" :animated="false" size="small" @on-click="switchTab">
          <TabPane label="Message" name="msg"></TabPane>
          <TabPane label="Raw" name="raw"></TabPane>
        </Tabs>
      </Col>
    </Row>
    <div v-if="eventDetail">
      <div v-if="currentTab==='msg'">
        <pre class="event-message">{{JSON.parse(eventDetail).message}}</pre>
      </div>
      <code-editor
        v-if="currentTab==='raw'"
        language="json"
        :content="eventDetail"
        class="event-detail"
      ></code-editor>
    </div>
  </div>
</template>

<script>
import CodeEditor from '@/components/CodeEditor.vue'

export default {
  components: {
    CodeEditor
  },
  data () {
    return {
      currentTab: 'msg'
    }
  },
  computed: {
    eventDetail () {
      return this.$store.state.event.eventDetail
    }
  },
  methods: {
    switchTab (tabName) {
      this.currentTab = tabName
    },
    dismiss () {
      this.$store.commit('setEventDetail', null)
    }
  }
}
</script>

<style lang="css">
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
.event-detail {
  height: calc(100vh - 172px);
  /* total:100vh
    header 38px
    button-bar 38px
    mode-tab 34px
    message-tab 34px
    footer 28px
    */
}
</style>

<style scoped>
.event-message {
  padding-left: 15px;
}
</style>
