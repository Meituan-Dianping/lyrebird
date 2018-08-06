<template>
    <card v-if="flowDetail">
        <tabs :value="currentTab" :animated="false" @on-click="switchTab">
            <tab-pane label="Request" name="req"></tab-pane>
            <tab-pane label="RequestBody" name="req-body"></tab-pane>
            <tab-pane label="Response" name="resp"></tab-pane>
            <tab-pane label="ResponseBody" name="resp-body"></tab-pane>
        </tabs>
        <code-editor v-if="flowDetail" :language="codeType" :content="codeContent" style="height: 500px"></code-editor>
    </card>
</template>

<script>
    module.exports = {
        props: {
            flow: null
        },
        data: function () {
            return {
                flowDetail: null,
                codeContent: null,
                codeType: 'json',
                currentTab: 'req'
            }
        },
        watch: {
            flow: function () {
                console.log('FlowDetail: flow changed');
                this.getFlowDetail(this.flow.id);
            }
        },
        methods: {
            getFlowDetail: function (flowID) {
                this.$http.get('/api/flow/' + flowID)
                    .then(response => {
                        this.flowDetail = response.data;
                        this.switchTab('req');
                    }, error => {
                        console.log('FlowDetail: get detail failed', error);
                    });
            },
            switchTab: function (name) {
                console.log('FLowDetail:switchTab', name);
                this.currentTab = name;
                if (name === 'req') {
                    this.codeContent = JSON.stringify(this.flowDetail.request, null, 4);
                    this.codeType = 'json';
                } else if (name === 'req-body') {
                    if (this.flowDetail.request.data) {
                        this.codeContent = JSON.stringify(this.flowDetail.request.data, null, 4);
                        this.codeType = 'json';
                    } else {
                        this.codeContent = '';
                        this.codeType = 'text';
                    }
                } else if (name === 'resp') {
                    this.codeContent = JSON.stringify(this.flowDetail.response, null, 4);
                    this.codeType = 'json';
                } else if (name === 'resp-body') {
                    if (this.flowDetail.response.data === null) {
                        this.codeContent = '';
                        this.codeType = 'text';
                        return;
                    }
                    if (this.flowDetail.response.headers.hasOwnProperty('Content-Type')) {
                        let contentType = this.flowDetail.response.headers['Content-Type'];
                        if (contentType.includes('html')) {
                            this.parseHtmlData(this.flowDetail.response.data);
                        } else if (contentType.includes('xml')) {
                            this.parseXmlData(this.flowDetail.response.data);
                        } else if (contentType.includes('json')) {
                            this.parseJsonData(this.flowDetail.response.data);
                        } else {
                            this.parseTextData(this.flowDetail.response.data);
                        }
                    } else {
                        this.parseTextData(this.flowDetail.response.data);
                    }
                }
            },
            parseJsonData: function (data) {
                this.codeContent = JSON.stringify(data, null, 4);
                this.codeType = 'json';
            },
            parseHtmlData: function (data) {
                this.codeContent = this.flowDetail.response.data;
                this.codeType = 'html';
            },
            parseXmlData: function (data) {
                this.codeContent = this.flowDetail.response.data;
                this.codeType = 'xml';
            },
            parseTextData: function (data) {
                this.codeContent = this.flowDetail.response.data;
                this.codeType = 'text';
            }
        },
        components: {
            'code-editor': httpVueLoader('static/vue/code-editor.vue')
        }
    };
</script>

<style>
</style>