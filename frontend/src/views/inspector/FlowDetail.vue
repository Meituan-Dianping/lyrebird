<template>
  <div>
    <v-container class="pa-0 data-list-button-bar">
      <v-row no-gutters >
        <v-tabs
          v-model="currentTab"
          center-active
          active-class="flow-detail-active-tab"
          background-color="shading"
          color="accent"
          height="29"
          show-arrows="never"
          slider-color="primary"
        >
          <v-btn icon plain title='Close' class="mx-2 flow-detail-close-button">
            <v-icon
              color="context"
              @click="dismiss"
              size="14px"
            >mdi-chevron-right-circle</v-icon>
          </v-btn>

          <v-tab append href="#req" class="flow-detail-tab">Request</v-tab>
          <v-tab append href="#req-body" class="flow-detail-tab">RequestBody</v-tab>
          <v-tab append href="#resp" class="flow-detail-tab">Response</v-tab>
          <v-tab append href="#resp-body" class="flow-detail-tab">ResponseBody</v-tab>
          <v-tab v-if="showProxyResponse" append href="#proxy-resp-diff" class="flow-detail-tab">ResponseBodyDiff</v-tab>
          <v-spacer />

          <JsonpathInfo :jsonpath="jsonPath" />
        </v-tabs>
      </v-row>
    </v-container>

    <span v-if="flowDetail">
      <Row style="background:#ffffff;margin-left:10px;" v-if="isDiffEditor" >
        <Col span="12">Mock Response</Col>
        <Col span="12">Proxy Response</Col>
      </Row>
      <CodeDiffEditor 
        v-if="isDiffEditor"
        :content="codeContent"
        :diffContent="diffContent"
        :language="codeType"
        class="flow-detail"
      />
      <CodeEditor
        v-else
        class="flow-detail"
        :language="codeType"
        :content="codeContent"
        v-on:on-jsonpath-change="onJsonPathChange"
      />
    </span>
    <div v-else class="flow-detail-empty">
      <v-icon large>mdi-package-variant-closed</v-icon>
      <p>No Selected flow</p>
    </div>

  </div>
</template>

<script>
import CodeEditor from '@/components/CodeEditor.vue'
import CodeDiffEditor from '@/components/CodeDiffEditor.vue'
import JsonpathInfo from '@/views/inspector/JsonpathInfo.vue'

export default {
  name: 'flowDetail',
  components: {
    CodeEditor,
    CodeDiffEditor,
    JsonpathInfo
  },
  data () {
    return {
      codeType: 'json',
      currentTab: 'req',
      jsonPath: null
    }
  },
  computed: {
    flowDetail () {
      return this.$store.state.inspector.focusedFlowDetail
    },
    codeContent () {
      let codeContent = ''
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
      return this.parseResponseByContentType(this.flowDetail.proxy_response)
    },
    isDiffEditor () {
      return this.currentTab === 'proxy-resp-diff'
    },
    showProxyResponse () {
      const isShow = this.flowDetail && this.flowDetail.hasOwnProperty('proxy_response')
      if (!isShow && this.currentTab == 'proxy-resp-diff') {
          this.currentTab = 'resp-body'
      }
      return isShow
    },
  },
  methods: {
    dismiss () {
      this.$store.commit('setInspectorSplit', 1)
      this.$store.commit('setFocusedFlowDetail', null)
      this.jsonPath = null
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
      let contentType = null
      for (const headerKey in response.headers) {
        if (headerKey.toLowerCase() == 'content-type') {
          contentType = response.headers[headerKey]
          break
        }
      }
      let codeContent = ''
      if (response.data === undefined || response.data === null) {
        codeContent = this.parseNullData(response.data)
      } else if (contentType) {
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
    },
    onJsonPathChange (payload) {
      this.jsonPath = payload.jsonPath
    }
  }
}
</script>

<style lang="css">
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
.flow-detail-tabs {
  border-bottom: 1px solid rgba(0,0,0,.12);
}
.flow-detail-close-button {
  height: 29px !important;
}
.flow-detail-tab {
  font-size: 12px;
  padding: 0px 12px;
  min-width: 0px;
}
.flow-detail-active-tab {
  font-weight: bold;
}
.flow-detail {
  height: calc(100vh - 44px - 40px - 38px - 33px - 28px - 12px);
  /* total:100vh
    header 44px
    title 40px
    head-line: 38px
    button-bar: 33px
    footer 28px
    margin-bottom: 12px
    */
}
.flow-detail-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
.v-slide-group__content {
  transform: none !important;
}
</style>
