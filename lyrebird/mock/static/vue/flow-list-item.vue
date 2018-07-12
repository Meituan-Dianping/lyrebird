<template>
    <tr>
        <td>
            <strong><span :class="[responseSrcClass]">{{responseSrc}}</span></strong>
        </td>
        <td>
            <strong><span :class="[codeClass]" >{{flow.response.code}}</span></strong>
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
    props: ['flow'],
    computed: {
        flowContent: function(){
            let urlParser = document.createElement('a');
            urlParser.href = this.flow.request.url;
            return urlParser;
        },
        codeClass: function(){
            let code = this.flow.response.code;
            if(code===200 || (code>=300 && code<=399)){
                return 'text-success';
            }else{
                return 'text-danger';
            }
        },
        responseSrc: function(){
            let respSrc = this.flow.response.mock;
            if(respSrc.includes('mock')){
                return 'mock'
            }else if(respSrc.includes('proxy')){
                return 'proxy'
            }else{
                return 'unknown'
            }
        },
        responseSrcClass: function(){
            let respSrc = this.flow.response.mock;
            if(respSrc.includes('mock')){
                return 'text-success'
            }else if(respSrc.includes('proxy')){
                return 'text-warning'
            }else{
                return 'text-danger'
            }
        }
    },
    methods: {
    }
}
</script>

<style>

</style>