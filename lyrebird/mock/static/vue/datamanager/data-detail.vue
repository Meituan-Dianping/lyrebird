<template>
    <card>
        <tabs :value="currentTab" :animated="false" @on-click="switchTab">
            <tab-pane label="Rule" name="rule"></tab-pane>
            <tab-pane label="Request" name="req"></tab-pane>
            <tab-pane label="RequestBody" name="req-body"></tab-pane>
            <tab-pane label="Response" name="resp"></tab-pane>
            <tab-pane label="ResponseBody" name="resp-body"></tab-pane>
        </tabs>
        <code-editor v-if="dataDetail" :language="codeType" :content="codeContent" style="height: 500px"></code-editor>
    </card>
</template>

<script>
    module.exports = {
        components: {
            'code-editor': httpVueLoader('static/vue/code-editor.vue')
        },
        data(){
            return {
                codeContent: null,
                codeType: 'json',
                currentTab: 'rule'
            }
        },
        computed: {
            dataDetail(){
                return this.$store.state.dataManager.dataDetail
            }
        },
        methods: {
            switchTab(name){
                console.log('Tab switch ->', name);
                if(name==='rule'){

                }else if(name==='req'){
                    this.codeContent = JSON.stringify(this.dataDetail.request, null, 4);
                    this.codeType = 'json';
                }else if(name==='req-body'){
                    if (this.dataDetail.request.data) {
                        this.codeContent = JSON.stringify(this.dataDetail.request.data, null, 4);
                        this.codeType = 'json';
                    } else {
                        this.codeContent = '';
                        this.codeType = 'text';
                    }
                }else if(name==='resp'){
                    this.codeContent = JSON.stringify(this.dataDetail.response, null, 4);
                    this.codeType = 'json';
                }else if(name==='resp-body'){
                    if (this.dataDetail.response.data === null) {
                        this.codeContent = '';
                        this.codeType = 'text';
                        return;
                    }
                    if (this.dataDetail.response.headers.hasOwnProperty('Content-Type')) {
                        let contentType = this.dataDetail.response.headers['Content-Type'];
                        if (contentType.includes('html')) {
                            this.parseHtmlData(this.dataDetail.response.data);
                        } else if (contentType.includes('xml')) {
                            this.parseXmlData(this.dataDetail.response.data);
                        } else if (contentType.includes('json')) {
                            this.parseJsonData(this.dataDetail.response.data);
                        } else {
                            this.parseTextData(this.dataDetail.response.data);
                        }
                    } else {
                        this.parseTextData(this.dataDetail.response.data);
                    }
                }
            },
            parseJsonData: function (data) {
                this.codeContent = JSON.stringify(data, null, 4);
                this.codeType = 'json';
            },
            parseHtmlData: function (data) {
                this.codeContent = this.dataDetail.response.data;
                this.codeType = 'html';
            },
            parseXmlData: function (data) {
                this.codeContent = this.dataDetail.response.data;
                this.codeType = 'xml';
            },
            parseTextData: function (data) {
                this.codeContent = this.dataDetail.response.data;
                this.codeType = 'text';
            }
        }
    }
</script>