<template>
  <div class="small-tab">
    <tabs v-model="currentTab" :animated="false" size="small">
      <tab-pane label="Information" name="info" />
      <tab-pane label="Request" name="req" />
      <tab-pane label="RequestData" name="reqdata" />
      <tab-pane label="Response" name="resp" />
      <tab-pane label="ResponseData" name="repdata" />
    </tabs>
    <div>
      <component :is="getDetailComponentNameByCurrentTab"></component>
    </div>
  </div>
</template>

<script>
import DataDetailInfo from '@/views/datamanager/DataDetailInfo.vue'
import CodeEditor from '@/components/CodeEditor.vue'
import Icon from 'vue-svg-icon/Icon.vue'

export default {
  components: {
    DataDetailInfo,
    CodeEditor,
    'svg-icon': Icon
  },
  data () {
    return {
      currentTab: 'info'
    }
  },
  computed: {
    getDetailComponentNameByCurrentTab () {
      if (this.currentTab === 'info') {
        return 'DataDetailInfo'
      } else {
        return 'CodeEditor'
      }
    }
  },
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
