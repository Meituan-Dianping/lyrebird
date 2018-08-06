<template>
    <tr>
        <td>
            <input type="checkbox" :id="flow.id" v-model="selected">
        </td>
        <td>
            <span class="label" :class="[responseSrcClass]">{{responseSrc}}</span>
        </td>
        <td>
            <strong>
                <span :class="[codeClass]">{{flow.response.code}}</span>
            </strong>
        </td>
        <td>
            {{flowContent.hostname}}
        </td>
        <td>
            {{flowContent.pathname}}
        </td>
    </tr>
</template>

<script>
    module.exports = {
        props: ['flow', 'selectedIds'],
        data: function () {
            return {
                selected: false
            }
        },
        watch: {
            selectedIds: function () {
                this.selected = this.selectedIds.indexOf(this.flow.id) >= 0
            },
            selected: function () {
                this.$emit('item-checkbox-change', {
                    id: this.flow.id,
                    selected: this.selected
                })
            }
        },
        computed: {
            flowContent: function () {
                let urlParser = document.createElement('a');
                urlParser.href = this.flow.request.url;
                return urlParser;
            },
            codeClass: function () {
                let code = this.flow.response.code;
                if (code === 200 || (code >= 300 && code <= 399)) {
                    return 'text-success';
                } else {
                    return 'text-danger';
                }
            },
            responseSrc: function () {
                let respSrc = this.flow.response.mock;
                if (respSrc.includes('mock')) {
                    return 'mock'
                } else if (respSrc.includes('proxy')) {
                    return 'proxy'
                } else {
                    return 'unknown'
                }
            },
            responseSrcClass: function () {
                let respSrc = this.flow.response.mock;
                if (respSrc.includes('mock')) {
                    return 'label-success'
                } else if (respSrc.includes('proxy')) {
                    return 'label-default'
                } else {
                    return 'label-danger'
                }
            }
        },
        methods: {}
    }
</script>

<style>
</style>