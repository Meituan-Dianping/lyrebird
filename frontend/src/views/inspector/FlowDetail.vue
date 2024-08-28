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
          <v-tab append href="#reqData" class="flow-detail-tab">RequestBody</v-tab>
          <v-tab append href="#resp" class="flow-detail-tab">Response</v-tab>
          <v-tab append href="#respData" class="flow-detail-tab">ResponseData</v-tab>
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
        :content="editorCache"
        :diffContent="diffContent"
        :language="currentTabContentType"
        class="flow-detail"
      />
      <CodeEditor
        v-else
        class="flow-detail"
        :language="currentTabContentType"
        v-model="editorContent"
        v-on:on-jsonpath-change="onJsonPathChange"
      />
    </span>
    <div v-else class="flow-detail-empty">
      <v-icon large>mdi-package-variant-closed</v-icon>
      <p>No Selected flow</p>
    </div>

    <div v-show="flowDetail" class="save-btn">
      <v-btn
        fab
        dark
        color="primary"
        class="save-btn-detail"
        @click="TemporaryMock"
      >
        M
      </v-btn>
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
      editorCache: {
        id: null,
        req: null,
        reqData: null,
        resp: null,
        respData: null
      },
      editorCacheLanguage: {
        req: 'json',
        reqData: null,
        resp: 'json',
        respData: null
      },
      codeType: 'json',
      currentTab: 'req',
      jsonPath: null,
    }
  },
  mounted () {
    this.setDataDetailEditorCache(this.flowDetail)
  },
  computed: {
    flowDetail () {
      return this.$store.state.inspector.focusedFlowDetail
    },
    editorContent: {
      get () {
        const content = this.editorCache[this.currentTab]
        if (!content) {
          return ''
        }
        return content
      },
      set (val) {
        this.editorCache[this.currentTab] = val
      }
    },
    currentTabContentType () {
      const content = this.editorCacheLanguage[this.currentTab]
      return content ? content : 'json'
    },
    diffContent () {
      return this.getParsedContentAndType(this.flowDetail.proxy_response)
    },
    isDiffEditor () {
      return this.currentTab === 'proxy-resp-diff'
    },
    showProxyResponse () {
      const isShow = this.flowDetail && this.flowDetail.hasOwnProperty('proxy_response')
      if (!isShow && this.currentTab == 'proxy-resp-diff') {
        this.currentTab = 'respData'
      }
      return isShow
    },
  },
  watch: {
    flowDetail (val) {
      this.setDataDetailEditorCache(val)
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
    setDataDetailEditorCache (val) {
      if (val === null || Object.keys(val).length === 0) {
        return
      }
      this.editorCache.id = val.id
      this.editorCache.req = JSON.stringify({
        ...val.request
      })
      let reqContentInfo = this.getParsedContentAndType(val.request)
      this.editorCache.reqData = reqContentInfo.content
      this.editorCacheLanguage.reqData = reqContentInfo.language

      this.editorCache.resp = JSON.stringify({
        code: val.response.code,
        headers: val.response.headers
      })
      let respContentInfo = this.getParsedContentAndType(val.response)
      this.editorCache.respData = respContentInfo.content
      this.editorCacheLanguage.respData = respContentInfo.language
    },
    parseNullData (_) {
      return ''
    },
    parseJsonData (data) {
      if (typeof data === 'object') {
        return JSON.stringify(data, null, 4)
      } else {
        return data
      }
    },
    parseHtmlData (data) {
      return data
    },
    parseXmlData (data) {
      return data
    },
    parseTextData (data) {
      return data
    },
    getParsedContentAndType (response) {
      let contentType = null
      for (const headerKey in response.headers) {
        if (headerKey.toLowerCase() == 'content-type') {
          contentType = response.headers[headerKey]
          break
        }
      }

      let contentInfo = { content: '', language: '' }

      if (!contentType) {
        contentInfo.language = 'json'
      } else if (response.data === undefined || response.data === null) {
        contentInfo.content = this.parseNullData(response.data)
        contentInfo.language = 'text'
      } else if (contentType.includes('json')) {
        contentInfo.content = this.parseJsonData(response.data)
        contentInfo.language = 'json'
      } else if (contentType.includes('html')) {
        contentInfo.content = this.parseHtmlData(response.data)
        contentInfo.language = 'html'
      } else if (contentType.includes('xml')) {
        contentInfo.content = this.parseXmlData(response.data)
        contentInfo.language = 'xml'
      } else {
        contentInfo.content = this.parseTextData(response.data)
        contentInfo.language = 'text'
      }
      return contentInfo
    },
    onJsonPathChange (payload) {
      this.jsonPath = payload.jsonPath
    },
    TemporaryMock () {
      const newData = {}
      // Add request
      const newReq = {}
      Object.assign(newReq, JSON.parse(this.editorCache.req))
      newReq['data'] = this.editorCache.reqData
      newData['request'] = newReq
      // Add response
      const newResp = {}
      Object.assign(newResp, JSON.parse(this.editorCache.resp))
      newResp['data'] = this.editorCache.respData
      newData['response'] = newResp

      newData.id = this.editorCache.id
      newData['lyrebirdInternalFlow'] = 'tempmock'

      this.$store.dispatch('createTempMockData', newData)
    },
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
