<template>
    <card>
        <tabs v-model="currentTab" :animated="false">
            <tab-pane label="Rule" name="rule"></tab-pane>
            <tab-pane label="Request" name="req"></tab-pane>
            <tab-pane label="RequestBody" name="req-body"></tab-pane>
            <tab-pane label="Response" name="resp"></tab-pane>
            <tab-pane label="ResponseBody" name="resp-body"></tab-pane>
        </tabs>
        <code-editor v-if="dataDetail" :language="code.type" :content="code.content" style="height: 500px"></code-editor>
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
                    
                }
                else if(this.currentTab === 'req'){
                    codeObj.content = JSON.stringify(this.dataDetail.request, null, 4)
                }
                else if(this.currentTab === 'req-body'){
                    let request = this.dataDetail.request
                    if(request.hasOwnProperty('data')){
                        codeObj = this.parseBody(request.headers, request.data)
                    }
                }
                else if(this.currentTab === 'resp'){
                    codeObj.content = JSON.stringify(this.dataDetail.response, null, 4)
                }
                else if(this.currentTab === 'resp-body'){
                    response = this.dataDetail.response
                    if(response.hasOwnProperty('data')){
                        codeObj = this.parseBody(response.headers, response.data)
                    }
                }
                return codeObj
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
                    parsedBody.type = 'text'
                    parsedBody.content = body
                }
                return parsedBody
            }
        }
    }
</script>