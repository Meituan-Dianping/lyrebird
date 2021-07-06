<template>
  <div v-if="flowDetail">
    <Row type="flex" justify="center" align="middle">
      <Col span="1">
        <Button icon="ios-arrow-dropright-circle" type="text" size="small" @click="dismiss"></Button>
      </Col>
      <Col span="23" class="small-tab">
        <Tabs :value="currentTab" :animated="false" size="small" @on-click="switchTab">
          <TabPane label="Request" name="req"></TabPane>
          <TabPane label="RequestBody" name="req-body"></TabPane>
          <TabPane label="Response" name="resp"></TabPane>
          <TabPane label="ResponseBody" name="resp-body"></TabPane>
          <TabPane v-if="showProxyResponse" label="ProxyResponseBody" name="proxy-resp-diff" />
          <!-- <TabPane v-if="showResponseDiff" label="ProxyResponseDiff" name="resp-diff" /> -->
        </Tabs>
      </Col>
    </Row>
    <code-editor v-if="flowDetail && isEditor" :language="codeType" :content="codeContent" class="flow-detail"></code-editor>
    <code-diff-editor v-if="flowDetail && isDiffEditor" :language="codeType" :content="codeContent" :diffContent="diffContent" class="flow-detail"></code-diff-editor>
  </div>
</template>

<script>
import CodeEditor from '@/components/CodeEditor.vue'
import CodeDiffEditor from '@/components/CodeDiffEditor.vue'
import FlowInspector from '@/views/inspector/FlowInspector.vue'

export default {
  name: 'flowDetail',
  components: {
    CodeEditor,
    CodeDiffEditor,
  },
  data () {
    return {
      codeType: 'json',
      currentTab: 'req'
    }
  },
  computed: {
    flowDetail () {
      return this.$store.state.inspector.focusedFlowDetail
    },
    codeContent () {
      let codeContent = ''
      let diffContent = ''
      if (this.currentTab === 'req') {
        codeContent = JSON.stringify(this.flowDetail.request, null, 4)
        this.codeType = 'json'
      } else if (this.currentTab === 'req-body') {
        if (this.flowDetail.request.data) {
          codeContent = this.parseJsonData(this.flowDetail.request.data)
          this.codeType = 'json'
        } else {
          codeContent = ''
          this.codeType = 'text'
        }
      } else if (this.currentTab === 'resp') {
        const respInfo = {
          code: this.flowDetail.response.code,
          headers: this.flowDetail.response.headers
        }
        codeContent = JSON.stringify(respInfo, null, 4)
        this.codeType = 'json'
      } else if (this.currentTab === 'resp-body') {
        codeContent = this.parseResponseByContentType(this.flowDetail.response)
      } else if (this.currentTab === 'proxy-resp-diff') {
        codeContent = this.parseResponseByContentType(this.flowDetail.response)
      } else { }
      return codeContent
    },
    diffContent () {
      let diffContent = ''
      if (this.currentTab === 'proxy-resp-diff') {
        diffContent = this.parseResponseByContentType(this.flowDetail.proxy_response)
      }
      return diffContent
    },
    isDiffEditor () {
      return this.currentTab === 'proxy-resp-diff'
    },
    isEditor () {
      return this.currentTab != 'proxy-resp-diff'
    },
    showProxyResponse () {
      if (!this.flowDetail.hasOwnProperty('proxy_response') && this.currentTab == 'proxy-resp-diff') {
        this.currentTab = 'resp-body'
      }
      return this.flowDetail.hasOwnProperty('proxy_response')
    },
  },
  methods: {
    dismiss () {
      this.$store.commit('setFocusedFlowDetail', null)
    },
    switchTab (name) {
      this.currentTab = name
    },
    parseNullData (data) {
      this.codeType = 'text'
      return ''
    },
    parseJsonData (data) {
      this.codeType = 'json'
      if (typeof data === 'object') {
        return JSON.stringify(data, null, 4)
      } else {
        return data
      }
    },
    parseHtmlData (data) {
      this.codeType = 'html'
      return data
    },
    parseXmlData (data) {
      this.codeType = 'xml'
      return data
    },
    parseTextData (data) {
      this.codeType = 'text'
      return data
    },
    parseResponseByContentType (response) {
      let codeContent = ''
      if (response.data === null) {
        codeContent = this.parseNullData(response.data)
      } else if (response.headers.hasOwnProperty('Content-Type')) {
        let contentType = response.headers['Content-Type']
        if (contentType.includes('html')) {
          codeContent = this.parseHtmlData(response.data)
        } else if (contentType.includes('xml')) {
          codeContent = this.parseXmlData(response.data)
        } else if (contentType.includes('json')) {
          codeContent = this.parseJsonData(response.data)
        } else {
          codeContent = this.parseTextData(response.data)
        }
      } else {
        codeContent = this.parseTextData(response.data)
      }
      return codeContent
    }
  }
}
</script>

<style lang="css">
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
.flow-detail {
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
