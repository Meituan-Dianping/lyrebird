<template>
  <div>
    <Row type="flex" justify="center" align="middle">
      <Col span="1">
        <Button icon="ios-arrow-dropright-circle" type="text" size="small" @click="dismiss"></Button>
      </Col>
      <Col span="23" class="small-tab">
        <Tabs :value="currentTab" :animated="false" size="small" @on-click="switchTab">
          <TabPane label="Raw" name="raw"/>
          <TabPane label="Message" name="msg"/>
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
      currentTab: 'raw'
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
  height: calc(100vh - 44px - 40px - 34px - 28px - 12px);
  /* total:100vh
    header 44px
    title 40px
    message-tab 34px
    margin-bottom: 12px
    footer 28px
    */
}
.event-message {
  width: 100%;
  height: calc(100vh - 44px - 40px - 34px - 28px - 12px);
  /* total:100vh
    header 44px
    title 40px
    message-tab 34px
    margin-bottom: 12px
    footer 28px
    */
  overflow: auto;
  margin: 0px;
  padding: 5px 0 0px 10px;
}
</style>
