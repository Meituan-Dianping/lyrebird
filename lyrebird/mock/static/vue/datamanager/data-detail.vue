<template>
    <card>
        <tabs :value="currentTab" :animated="false" @on-click="switchTab">
            <tab-pane label="Rule" name="rule"></tab-pane>
            <tab-pane label="Request" name="req"></tab-pane>
            <tab-pane label="RequestBody" name="req-body"></tab-pane>
            <tab-pane label="Response" name="resp"></tab-pane>
            <tab-pane label="ResponseBody" name="resp-body"></tab-pane>
        </tabs>
        <code-editor v-if="flowDetail" :language="codeType" :content="codeContent" style="height: 500px"></code-editor>
    </card>
</template>
