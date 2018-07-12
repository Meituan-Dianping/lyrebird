<template>
    <div>
        <div id="code-editor" style="width:100%;height:100%;border:1px solid grey"></div>
    </div>
</template>

<script>
module.exports = {
    props: {
        'content': null, 
        'language':{
            default: 'javascript'
        },
        'readOnly':{
            default: false
        }
    },
    data: function(){
        return {
            editor: null
        }
    },
    watch:{
        content: function(){
            console.log("Code editor: content change");
            window.monaco.editor.setModelLanguage(this.editor.getModel(), this.language);
            this.editor.setValue(this.content);            
            // let action = this.editor.getAction('editor.action.formatDocument')
            // if(action){
            //     action.run();
            //     console.log('Run action', action);            
            // }
            this.editor.trigger(this.editor.getValue(), 'editor.action.formatDocument')
        }
    },
    mounted: function(){
        this.editor = window.monaco.editor.create(
            this.$el.querySelector('#code-editor'), 
            {
                value: this.content,
                language: this.language,
                theme: 'vs',
                readOnly: this.readOnly
            }
        );
    }
};
</script>

<style>
</style>