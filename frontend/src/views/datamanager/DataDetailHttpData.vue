<template>
  <div class="small-tab">
    <tabs @on-click="onRespDataTabClick" v-model="currentTab" :animated="false" size="small">
      <tab-pane label="Information" name="info" />
      <tab-pane label="Request" name="req" />
      <tab-pane label="RequestData" name="reqData" />
      <tab-pane label="Response" name="resp" />
      <tab-pane label="ResponseData" name="respData" />
    </tabs>
    <div>
      <CodeEditor
        v-if="!isShowCodeDiffEditor"
        class="data-detail"
        :language="currentTabContentType"
        v-model="editorContent"
        v-on:on-jsonpath-change="onJsonPathChange"
      ></CodeEditor>
      <CodeDiffEditor
        v-if="isShowCodeDiffEditor"
        class="data-detail"
        :language="currentTabContentType"
        :content="editorContent"
        :diffContent="editorDiffContent"
        :readOnly="true"
      ></CodeDiffEditor>
    </div>
    <div class="save-btn" v-if="dataDetail">
      <!-- <v-tooltip top>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            v-bind="attrs"
            v-on="on"
            fab
            dark
            color="primary"
            class="save-btn-detail"
            @click="save"
          >
            <v-icon
            class="save-btn-icon"
            dark>
              mdi-content-save-outline
            </v-icon>
          </v-btn>
        </template>
        <span>Save (⌘+s)</span>
      </v-tooltip> -->

      <!-- <v-card id="create"> -->
      <v-speed-dial
        :open-on-hover="true"
      >
        <template v-slot:activator>
          <v-btn
            color="primary"
            dark
            fab
            class="save-btn-detail"
            @click="save"
            title="Save (⌘+s)"
          >
            <v-icon
            class="save-btn-icon"
            dark>
              mdi-content-save-outline
            </v-icon>
          </v-btn>
        </template>
        <v-btn
          fab
          dark
          small
          color="primary"
          class="save-btn-detail"
          :value="currentTab"
          @click="showDiff"
          title="Show the differences"
        >
          <v-icon>mdi-eye-outline</v-icon>
        </v-btn>
        <v-btn
          fab
          dark
          small
          color="primary"
          class="save-btn-detail"
          :value="currentTab"
          @click="hideDiff"
          title="Hide the differences"
        >
          <v-icon>mdi-eye-off-outline</v-icon>
        </v-btn>
      </v-speed-dial>
    <!-- </v-card> -->


    </div>
  </div>
</template>

<script>
import DataDetailInfo from '@/views/datamanager/DataDetailInfo.vue'
import CodeEditor from '@/components/CodeEditor.vue'
import Icon from 'vue-svg-icon/Icon.vue'
import CodeDiffEditor from '@/components/CodeDiffEditor.vue'

export default {
  components: {
    DataDetailInfo,
    CodeEditor,
    CodeDiffEditor,
    'svg-icon': Icon
  },
  data () {
    return {
      editorCache: {
        info: null,
        req: null,
        reqData: null,
        resp: null,
        respData: null,
      },
      isShowDiff: false,
    }
  },
  mounted () {
    this.$bus.$on('keydown', this.onKeyDown)
    this.setDataDetailEditorCache(this.dataDetail)
  },
  beforeDestroy () {
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
        const content = this.$store.state.dataManager.renderedRespData
        if (!content) {
          return ''
        }
        return content
      },
      set (val) {
        this.$store.commit('setRenderedRespData', val)
      }
    },
    isShowCodeDiffEditor() {
      if (this.currentTab === 'respData') {
        if (this.isShowDiff){
          return true
        }
      } else {
        return false
      }
    },
    isCurrentTabRespData () {
      if (this.currentTab === 'respData') {
        return true
      } else {
        return false
      }
    },
    isShowEye () {
      if (this.editorContent != this.editorDiffContent && !this.isShowDiff) {
        return true
      } else {
        return false
      }
    }
  },
  watch: {
    dataDetail (val) {
      this.setDataDetailEditorCache(val)
      this.onRespDataTabClick()
    },
  },
  methods: {
    save () {
      const newData = {}
      Object.assign(newData, JSON.parse(this.editorCache.info))
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

      this.$store.commit('setIsReloadTreeWhenUpdate', this.dataDetail.name !== newData.name)

      this.$store.dispatch('saveDataDetail', newData)
    },
    onJsonPathChange (payload) {
      this.$store.commit('setJsonPath', payload.jsonPath)
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
      this.editorCache.info = JSON.stringify({
        id: val.id,
        name: val.name,
        rule: val.rule
      })
      this.editorCache.req = JSON.stringify({
        url: val.request.url,
        headers: val.request.headers,
        method: val.request.method
      })
      this.editorCache.reqData = typeof (val.request.data) == 'object' ? JSON.stringify(val.request.data) : val.request.data
      this.editorCache.resp = JSON.stringify({
        code: val.response.code,
        headers: val.response.headers
      })
      this.editorCache.respData = typeof (val.response.data) == 'object' ? JSON.stringify(val.response.data) : val.response.data
    },
    onRespDataTabClick () {
        const responseData = this.editorCache.respData
        this.$store.dispatch('loadRenderedData', {'data': responseData})
        console.log("12333")
    },
    showDiff () {
      this.isShowDiff = true
    },
    hideDiff () {
      this.isShowDiff = false
    },
  }
}
</script>

<style scoped>
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
</style>
