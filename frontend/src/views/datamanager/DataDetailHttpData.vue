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

          <v-tab append href="#info" class="flow-detail-tab">Information</v-tab>
          <v-tab append href="#req" class="flow-detail-tab">Request</v-tab>
          <v-tab append href="#reqData" class="flow-detail-tab">RequestBody</v-tab>
          <v-tab append href="#resp" class="flow-detail-tab">Response</v-tab>
          <v-tab append href="#respData" class="flow-detail-tab">ResponseData</v-tab>
          <v-spacer />

          <JsonpathInfo :jsonpath="jsonPath" />
        </v-tabs>
      </v-row>
    </v-container>

    <div>
      <CodeEditor
        v-if="!isShowCodeDiffEditor"
        class="data-detail"
        :language="currentTabContentType"
        v-model="editorContent"
        v-on:on-jsonpath-change="onJsonPathChange" />
      <CodeDiffEditor
        v-else
        class="data-detail"
        :language="currentTabContentType"
        :content="editorContent"
        :diffContent="editorDiffContent" />
    </div>

    <div
      class="show-diff-btn"
      v-if="this.currentTab==='respData' && !this.isEditorContentEquals"
    >
      <v-tooltip top>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            v-bind="attrs"
            v-on="on"
            color="primary"
            dark
            fab
            class="save-btn-detail"
            @click="diffButtonClick"
          >
          <v-icon v-if="diffButtonStatus === 'show'">mdi-eye-outline</v-icon>
          <v-icon v-else>mdi-eye-off-outline</v-icon>
          </v-btn>
        </template>
        <span v-if="diffButtonStatus === 'show'">Show the diff</span>
        <span v-else>Hide the diff</span>
      </v-tooltip>
    </div>

    <div class="save-btn" v-if="dataDetail">
      <v-tooltip top>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            v-bind="attrs"
            v-on="on"
            color="primary"
            dark
            fab
            class="save-btn-detail"
            @click="save"
          >
            <v-icon
              class="save-btn-icon"
              dark
            >
              mdi-content-save-outline
            </v-icon>
          </v-btn>
        </template>
        <span>Save (⌘+s)</span>
      </v-tooltip>
    </div>

  </div>
</template>

<script>
import { parse, stringify } from 'lossless-json'
import DataDetailInfo from '@/views/datamanager/DataDetailInfo.vue'
import CodeEditor from '@/components/CodeEditor.vue'
import CodeDiffEditor from '@/components/CodeDiffEditor.vue'
import JsonpathInfo from '@/views/inspector/JsonpathInfo.vue'
import { render } from '@/api'

export default {
  components: {
    DataDetailInfo,
    CodeEditor,
    CodeDiffEditor,
    JsonpathInfo
  },
  data () {
    return {
      editorCache: {
        info: null,
        req: null,
        reqData: null,
        resp: null,
        respData: null
      },
      diffButtonStatus: 'show',
      isEditorContentEquals: true,
      isTreeNodeClicked: false,
      renderedRespData: '',
      jsonPath: null,
    }
  },
  mounted () {
    this.$bus.$on('keydown', this.onKeyDown)
    this.setDataDetailEditorCache(this.dataDetail)
  },
  beforeDestroy () {
    this.$bus.$off('keydown', this.onKeyDown)
  },
  activated () {
    this.$bus.$on('keydown', this.onKeyDown)
  },
  deactivated () {
    this.$bus.$off('keydown', this.onKeyDown)
  },
  computed: {
    currentTab: {
      get () {
        const dataDetailFocuedTab = this.$store.state.dataManager.dataDetailFocuedTab
        if (this.editorCache.hasOwnProperty(dataDetailFocuedTab)) {
          return dataDetailFocuedTab
        }
        return 'info'
      },
      set (val) {
        this.$store.commit('setDataDetailFocuedTab', val)
      }
    },
    currentTabContentType () {
      if (this.currentTab === 'info' || this.currentTab === 'req' || this.currentTab === 'resp') {
        return 'json'
      } else {
        return 'json'
      }
    },
    dataDetail () {
      return this.$store.state.dataManager.dataDetail
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
    editorDiffContent: {
      get () {
        const content = this.renderedRespData
        if (!content) {
          return ''
        }
        return content
      },
      set (val) {
        this.renderedRespData = val
      }
    },
    isShowCodeDiffEditor () {
      if (this.currentTab === 'respData') {
        if (this.diffButtonStatus === 'hide') {
          return true
        }
        return false
      }
      return false
    }
  },
  watch: {
    dataDetail (val) {
      this.setDataDetailEditorCache(val)
      this.updateDiffButtonStatus()
    },
  },
  methods: {
    save () {
      const newData = {}
      Object.assign(newData, parse(this.editorCache.info))
      // Add request
      const newReq = {}
      Object.assign(newReq, parse(this.editorCache.req))
      newReq['data'] = this.editorCache.reqData
      newData['request'] = newReq
      // Add response
      const newResp = {}
      Object.assign(newResp, parse(this.editorCache.resp))
      newResp['data'] = this.editorCache.respData
      newData['response'] = newResp
      // Add Flag
      newData['lyrebirdInternalFlow'] = 'datamanager'

      this.$store.dispatch('saveDataDetail', newData)
    },
    onJsonPathChange (payload) {
      this.jsonPath = payload.jsonPath
    },
    onKeyDown (event) {
      if (event.code !== "KeyS" || !event.metaKey) {
        return
      }
      this.save()
      event.preventDefault()
      console.log("Save", event)
    },
    setDataDetailEditorCache (val) {
      if (val === null || Object.keys(val).length === 0) {
        return
      }
      this.editorCache.info = stringify({
        id: val.id,
        name: val.name,
        rule: val.rule,
        apiDiffConfig: val.apiDiffConfig
      })
      this.editorCache.req = stringify({
        url: val.request.url,
        headers: val.request.headers,
        method: val.request.method
      })
      this.editorCache.reqData = typeof (val.request.data) == 'object' ? stringify(val.request.data) : val.request.data
      this.editorCache.resp = stringify({
        code: val.response.code,
        headers: val.response.headers
      })
      this.editorCache.respData = typeof (val.response.data) == 'object' ? stringify(val.response.data) : val.response.data
    },
    loadEditorDiffContent () {
      const data = this.editorCache['respData']
      render(data)
        .then(response => {
          if (data != response.data.data) {
            this.isEditorContentEquals = false
            if (this.diffButtonStatus === 'hide'){
              this.renderedRespData = response.data.data
            }
          } else {
            this.isEditorContentEquals = true
          }
          if (this.isTreeNodeClicked) {
            this.diffButtonStatus = 'show'
            this.resetRenderedRespData()
          }
        }).catch(error => {
            bus.$emit('msg.error', 'Load rendered data error: ' + error.data.message)
        })
    },
    onTabClick () {
      if (this.currentTab === 'respData') {
        this.isTreeNodeClicked = false
        this.loadEditorDiffContent()
      } else {
        this.resetRenderedRespData()
      }
    },
    diffButtonClick () {
      this.isTreeNodeClicked = false
      if (this.diffButtonStatus === 'show') {
        this.diffButtonStatus = 'hide'
        this.loadEditorDiffContent()
      } else {
        this.diffButtonStatus = 'show'
        this.resetRenderedRespData()
      }
    },
    updateDiffButtonStatus() {
      if (this.currentTab === 'respData') {
        this.isTreeNodeClicked = true
        this.loadEditorDiffContent()
      }
    },
    resetRenderedRespData() {
      this.renderedRespData = ''
    }
  }
}
</script>

<style scoped>
.show-diff-btn {
  color: #fff;
  font-size: 0.6rem;
  text-align: center;
  line-height: 3rem;
  width: 3rem;
  height: 3rem;
  position: fixed;
  right: 60px;
  bottom: 140px;
  border-radius: 50%;
  z-index: 2;
}
</style>
