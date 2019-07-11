<template>
  <div>
    <div class="small-tab">
      <tabs v-model="currentTab" :animated="false" size="small">
        <tab-pane label="Information" name="information">
          <DataDetailInfo class="data-detail" :information="displayDataInfo"/>
        </tab-pane>
        <tab-pane v-for="(tab, index) in tabs" :label="tab.name" :key="tab.key" :name="tab.key" />
        <code-editor
          class="data-detail"
          v-if="currentTab !== 'information'"
          :language="code.type"
          v-model="content"
          v-on:on-jsonpath-change="onJsonPathChange"
        />
      </tabs>
      <div class="save-btn" v-if="dataDetail">
        <Tooltip content="Save" placement="top" :delay="500">
        <Button type="primary" shape="circle" @click="save">
          <icon name="md-save" scale="4"></icon>
        </Button>
        </Tooltip>
      </div>
    </div>
  </div>
</template>

<script>
import DataDetailInfo from "@/views/datamanager/DataDetailInfo.vue"
import CodeEditor from '@/components/CodeEditor.vue'
import Icon from 'vue-svg-icon/Icon.vue'

export default {
  components: {
    DataDetailInfo,
    CodeEditor,
    Icon
  },
  data() {
    return {
      currentTab: 'information',
      unshowInfoKey: ['request', 'requestData', 'response', 'responseData', 'children'],
    }
  },
  computed: {
    tabs() {
      return [
        {
          name: 'Request',
          key: 'req'
        },
        {
          name: 'RequestData',
          key: 'req-body'
        },
        {
          name: 'Response',
          key: 'resp'
        },
        {
          name: 'ResponseData',
          key: 'resp-body'
        }
      ]
    },
    originalDataDetail() {
      // data detail from api /api/data/<dataId>
      return this.$store.state.dataManager.dataDetail
    },
    dataDetail() {
      // display in frontend tab
      let displayDataDetail = {
        request: null,
        response: null
      }
      if (this.originalDataDetail.request && this.originalDataDetail.response) {
        displayDataDetail.request = this.originalDataDetail.request
        displayDataDetail.response = this.originalDataDetail.response
        if (this.originalDataDetail.request.hasOwnProperty('data')) {
          displayDataDetail.requestData = this.originalDataDetail.request.data
        }
        if (this.originalDataDetail.response.hasOwnProperty('data')) {
          displayDataDetail.responseData = this.originalDataDetail.response.data
        }
      } else { }
      return displayDataDetail
    },
    displayDataInfo() {
      // display in information
      let res = {}
      for (const key in this.originalDataDetail) {
        if (this.unshowInfoKey.indexOf(key) === -1 && key.substring(0,1) !== '_') {
          res[key] = this.originalDataDetail[key]
        }
      }
      return res
    },
    code() {
      let codeObj = {
        content: '',
        type: 'json'
      }
      if (this.currentTab === 'req') {
        codeObj.content = JSON.stringify(this.dataDetail.request, null, 4)
      } else if (this.currentTab === 'resp') {
        codeObj.content = JSON.stringify(this.dataDetail.response, null, 4)
      } else if (this.currentTab === 'req-body') {
        codeObj.content = this.dataDetail.requestData ? this.dataDetail.requestData : ''
        codeObj.type = this.dataDetail.requestData ? 'json' : 'text'
      } else if (this.currentTab === 'resp-body') {
        codeObj.content = this.dataDetail.responseData ? this.dataDetail.responseData : ''
        codeObj.type = this.dataDetail.responseData ? 'json': 'text'
      }
      return codeObj
    },
    content: {
      get() {
        return this.code.content
      },
      set(value) {
        const dataDetail = this.$store.state.dataManager.dataDetail
        if (this.currentTab === 'rule') {
          try {
            dataDetail.rule = JSON.parse(value)
          } catch (error) {
            console.error('Detail rule error')
            console.error(error)
          }
        } else if (this.currentTab === 'req') {
          dataDetail.request = value
        } else if (this.currentTab === 'req-body' && dataDetail.request_data) {
          dataDetail.request.data = value
        } else if (this.currentTab === 'resp') {
          dataDetail.response = value
        } else if (
          this.currentTab === 'resp-body' &&
          dataDetail.response.data
        ) {
          dataDetail.response.data = value
        }
        this.$store.commit('setDataDetail', dataDetail)
      }
    }
  },
  methods: {
    parseBody(headers, body) {
      let parsedBody = { type: 'text', content: '' }
      if (!headers.hasOwnProperty('Content-Type')) {
        return parsedBody
      }

      const contentType = headers['Content-Type']
      if (contentType.includes('html')) {
        parsedBody.type = 'html'
        parsedBody.content = body
      } else if (contentType.includes('json')) {
        parsedBody.type = 'json'
        parsedBody.content = JSON.stringify(body, null, 4)
      } else if (contentType.includes('xml')) {
        parsedBody.type = 'xml'
        parsedBody.content = body
      } else {
        try {
          parsedBody.content = JSON.stringify(body, null, 4)
          parsedBody.type = 'json'
        } catch (error) {
          parsedBody.type = 'text'
          parsedBody.content = 'Unreadable'
        }
      }
      return parsedBody
    },
    save() {
      this.$store.dispatch('saveDataDetail', this.dataDetail)
    },
    onJsonPathChange(payload) {
      this.$store.commit('setJsonPath', payload.jsonPath)
    }
  }
}
</script>

<style scoped>
.data-detail {
  height: calc(100vh - 150px);
  /* total:100vh
    header: 38px
    buttonBar: 28px
    tree
    footer: 28px
  */
}
.small-tab > .ivu-tabs > .ivu-tabs-bar {
  margin-bottom: 0;
}
.save-btn {
  color: #fff;
  font-size: 0.6rem;
  text-align: center;
  line-height: 3rem;
  width: 3rem;
  height: 3rem;
  position: fixed;
  right: 50px;
  bottom: 70px;
  border-radius: 50%;
  z-index: 500;
}
.save-btn > .ivu-tooltip > .ivu-tooltip-rel > .ivu-btn {
  padding: 5px 8px 5px;
  background-color: #0fccbf;
  border-color: #0fccbf;
}
</style>
