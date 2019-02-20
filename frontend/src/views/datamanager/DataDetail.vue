<template>
    <div class="small-tab">
        <tabs v-model="currentTab" :animated="false" size="small">
            <tab-pane label="Rule" name="rule"></tab-pane>
            <tab-pane label="Request" name="req"></tab-pane>
            <tab-pane label="RequestBody" name="req-body"></tab-pane>
            <tab-pane label="Response" name="resp"></tab-pane>
            <tab-pane label="ResponseBody" name="resp-body"></tab-pane>
        </tabs>
        <code-editor 
          v-if="dataDetail" 
          :language="code.type" 
          v-model="content" 
          class="data-detail"
          v-on:jsonpath="onDidChangeJsonPath"
          ></code-editor>
        <div class="save-btn" v-if="dataDetail">
            <Tooltip content="Save" placement="top" :delay="500">
            <Button type="primary" shape="circle" @click="save">
                <icon name="md-save" scale="4"></icon>
            </Button>
            </Tooltip>
        </div>
    </div>
</template>

<script>
import CodeEditor from '@/components/CodeEditor.vue'
import Icon from 'vue-svg-icon/Icon.vue'

export default{
    components:{
        CodeEditor,
        Icon
    },
    data(){
        return {
            currentTab: 'rule'
        }
    },
    computed: {
        dataDetail(){
            return this.$store.state.dataManager.dataDetail
        },
        code(){
            let codeObj = {
                content: '',
                type: 'json'
            }

            if(this.currentTab === 'rule'){
                codeObj.content = JSON.stringify(this.dataDetail.rule, null, 4)
                codeObj.type = 'json'
            }
            else if(this.currentTab === 'req'){
                codeObj.content = this.dataDetail.request.content
                codeObj.type = this.dataDetail.request.filetype
            }
            else if(this.currentTab === 'req-body'){
                if(this.dataDetail.request_data && this.dataDetail.request_data.content){
                    codeObj.content = this.dataDetail.request_data.content
                    codeObj.type = this.dataDetail.request_data.filetype
                }else{
                    codeObj.content = ''
                    codeObj.type = 'text'
                }
            }
            else if(this.currentTab === 'resp'){
                codeObj.content = this.dataDetail.response.content
                codeObj.type = this.dataDetail.response.filetype
            }
            else if(this.currentTab === 'resp-body'){
                if(this.dataDetail.response_data && this.dataDetail.response_data.content){
                    codeObj.content = this.dataDetail.response_data.content
                    codeObj.type = this.dataDetail.response_data.filetype
                }else{
                    codeObj.content = ''
                    codeObj.type = 'text'
                }
            }
            return codeObj
        },
        content: {
            get(){
                return this.code.content
            },
            set(value){
                const dataDetail = this.$store.state.dataManager.dataDetail
                if(this.currentTab==='rule'){
                    try {
                        dataDetail.rule = JSON.parse(value)                        
                    } catch (error) {
                        console.error('Detail rule error');
                        console.error(error);
                    }
                }else if(this.currentTab==='req'){
                    dataDetail.request.content = value
                }else if(this.currentTab==='req-body'){
                    dataDetail.request_data.content = value
                }else if(this.currentTab==='resp'){
                    dataDetail.response.content = value
                }else if(this.currentTab==='resp-body'){
                    dataDetail.response_data.content = value
                }
                this.$store.commit('setDataDetail', dataDetail)
            }
        }
    },
    methods: {
        parseBody(headers, body){
            let parsedBody = {type:'text', content:''}
            if(!headers.hasOwnProperty('Content-Type')){
                return parsedBody
            }

            const contentType = headers['Content-Type']
            if(contentType.includes('html')){
                parsedBody.type = 'html'
                parsedBody.content = body
            }else if(contentType.includes('json')){
                parsedBody.type = 'json'
                parsedBody.content = JSON.stringify(body, null, 4)
            }else if(contentType.includes('xml')){
                parsedBody.type = 'xml'
                parsedBody.content = body
            }else{
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
        save(){
            this.$store.dispatch('saveDataDetail', this.dataDetail)
        },
        onDidChangeJsonPath(payload) {
            this.$store.dispatch('updateJsonPath', payload.jsonPath)
        }
    }
}
</script>

<style scoped>
.button-bar{
    margin-top: 5px
}
.data-detail {
  height: calc(100vh - 150px);
  /* total:100vh
  header: 38px
  buttonBar: 38px
  tab-header: 52px
  table
  padding: 5px
  footer: 28px
    */
}
.small-tab > .ivu-tabs > .ivu-tabs-bar {
 margin-bottom: 0;
}
.save-btn {
    color:#fff;
    font-size: 0.6rem;
    text-align: center;
    line-height: 3rem;
    width:3rem;
    height:3rem;
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
