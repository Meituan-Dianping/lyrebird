<template>
  <div>
    <div class="small-tab">
      <tabs v-model="currentTab" :animated="false" size="small">
        <tab-pane v-if="tabs" v-for="(tab, index) in tabs" :label="tab.name" :key="tab.key" :name="tab.key">
          <component
            class="data-detail"
            :is="getComponentByType(tab)"
            :information="tab.value"
            :language="code.type" 
            v-model="content" 
            v-on:on-jsonpath-change="onJsonPathChange"
          />
        </tab-pane>
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
    }
  },
  computed: {
    tabs() {
      return [
        {
          name: 'Information',
          key: 'information',
          type: 'info',
          value: this.$store.state.dataManager.focusNodeDetail.information
        },
        {
          name: 'Request',
          key: 'req',
          type: 'code',
          value: ''
        },
        {
          name: 'RequestData',
          key: 'resp',
          type: 'code',
          value: ''
        },
        {
          name: 'Response',
          key: 'req-body',
          type: 'code',
          value: ''
        },
        {
          name: 'ResponseData',
          key: 'resp-body',
          type: 'code',
          value: ''
        }
      ]
    },
    dataDetail() {
      return this.$store.state.dataManager.focusNodeDetail
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
    },
    getComponentByType(payload) {
      if (payload.type === 'info') {
        return 'DataDetailInfo'
      } else if (payload.type === 'code') {
        return 'CodeEditor'
      } else {
        return 'DataDetailInfo'
      }
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
