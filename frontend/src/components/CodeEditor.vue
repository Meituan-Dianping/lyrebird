<template>
    <div>
        <div id="code-editor" style="width:100%;height:100%;border:1px solid grey"></div>
    </div>
</template>

<script>
import * as monaco from 'monaco-editor'

export default {
    name: 'codeEditor',
    model: {
        prop: 'content',
        event: 'change',
        event: 'change-cursor',
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
                    monaco.editor.setModelLanguage(this.editor.getModel(), this.language);
                    this.editor.setValue(newValue);
                    this.editor.trigger(this.editor.getValue(), 'editor.action.formatDocument')
                }
            }
            
        }
    },
    mounted: function(){
        const copyToClipboard = this.copyToClipboard
        this.editor = monaco.editor.create(
            this.$el.querySelector('#code-editor'), 
            {
                value: this.content,
                language: this.language,
                theme: 'vs',
                readOnly: this.readOnly
            }
        );
        this.editor.addAction({
            id: 'json-path',
            label: 'Copy JsonPath',
            keybindings: [
                monaco.KeyMod.chord(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_J)
            ],
            precondition: null,
            keybindingContext: null,
            contextMenuGroupId: 'navigation',
            contextMenuOrder: 1.5,
            run: copyToClipboard
        });
        this.editor.onDidChangeModelContent(event => {
            const value = this.editor.getValue()
            if (this.value !== value) {
                this.$emit('change', value, event)
            }
        })
        this.editor.onDidChangeCursorPosition(event => {
            const value = this.editor.getValue()
            const offSet = this.editor.getModel().getOffsetAt(event.position)
            const language = this.language;
            if (this.value !== value) {
                this.$emit('change-cursor', {offSet: offSet, content: value, language: language}, event)
            }
        })
    },
    methods:{
        copyToClipboard() {
            const notification = this.$Notice
            navigator.clipboard.writeText(this.$store.state.dataManager.jsonPath)
                .then(function() {
                    notification.success({
                        title: 'jsonpath copy successded.'
                    });
                }, function() {
                    notification.error({
                        title: 'jsonpath copy failed.'
                    });
                });
        }
    }
};
</script>

<style>
</style>