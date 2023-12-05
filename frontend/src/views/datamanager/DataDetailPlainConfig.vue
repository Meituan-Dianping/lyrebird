<template>
  <div class="small-tab">

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
          <v-tab append href="#json" class="flow-detail-tab">Settings</v-tab>
          <v-spacer />

          <JsonpathInfo :jsonpath="jsonPath" />
        </v-tabs>
      </v-row>
    </v-container>

    <div>
      <CodeEditor
        class="data-detail"
        :language="currentTabContentType"
        v-model="editorContent"
        v-on:on-jsonpath-change="onJsonPathChange"
      ></CodeEditor>
    </div>

    <div class="save-btn" v-if="dataDetail">
      <v-tooltip top>
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
      </v-tooltip>
    </div>
  </div>
</template>

<script>
import DataDetailInfo from '@/views/datamanager/DataDetailInfo.vue'
import CodeEditor from '@/components/CodeEditor.vue'
import JsonpathInfo from '@/views/inspector/JsonpathInfo.vue'

export default {
  components: {
    DataDetailInfo,
    CodeEditor,
    JsonpathInfo
  },
  data () {
    return {
      editorCache: {
        info: null,
        json: null
      }
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
      return 'json'
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
    }
  },
  watch: {
    dataDetail (val) {
      this.setDataDetailEditorCache(val)
    }
  },
  methods: {
    save () {
      const newData = {}
      Object.assign(newData, JSON.parse(this.editorCache.info))
      newData['json'] = this.editorCache.json
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
    },
    setDataDetailEditorCache (val) {
      if (val === null || Object.keys(val).length === 0) {
        return
      }
      this.editorCache.info = JSON.stringify({
        id: val.id,
        name: val.name
      })
      this.editorCache.json = typeof (val.json) == 'object' ? JSON.stringify(val.json) : val.json
    }
  }
}
</script>

<style scoped>
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
</style>
