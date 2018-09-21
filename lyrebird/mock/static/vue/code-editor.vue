<template>
    <div>
        <div id="code-editor" style="width:100%;height:100%;border:1px solid grey"></div>
    </div>
</template>

<script>
module.exports = {
    model: {
        prop: 'content',
        event: 'change'
    },
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
        content: function(newValue){
            console.log("Code editor: content change");
            if (this.editor) {
                if (newValue !== this.editor.getValue()) {
                    window.monaco.editor.setModelLanguage(this.editor.getModel(), this.language);
                    this.editor.setValue(newValue);
                    this.editor.trigger(this.editor.getValue(), 'editor.action.formatDocument')
                }
            }
            
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
        this.editor.onDidChangeModelContent(event => {
        const value = this.editor.getValue()
        if (this.value !== value) {
          this.$emit('change', value, event)
        }
      })
    }
};
</script>

<style>
</style>