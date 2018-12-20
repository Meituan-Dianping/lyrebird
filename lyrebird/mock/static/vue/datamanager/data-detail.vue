<template>
    <card>
        <tabs v-model="currentTab" :animated="false">
            <tab-pane label="Rule" name="rule"></tab-pane>
            <tab-pane label="Request" name="req"></tab-pane>
            <tab-pane label="RequestBody" name="req-body"></tab-pane>
            <tab-pane label="Response" name="resp"></tab-pane>
            <tab-pane label="ResponseBody" name="resp-body"></tab-pane>
        </tabs>
        <code-editor v-if="dataDetail" :language="code.type" v-model="content" style="height: 500px"></code-editor>
        <div v-if="dataDetail" class="button-bar">
            <i-button type="primary" ghost @click="save">Save</i-button>
        </div>
    </card>
</template>

<script>
    module.exports = {
        components: {
            'code-editor': httpVueLoader('static/vue/code-editor.vue')
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
                        dataDetail.rule = JSON.parse(value)
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
                this.$store.dispatch('saveDataDetail', dataDetail)
            }
        }
    }
</script>

<style>
.button-bar{
    margin-top: 5px
}
</style>
