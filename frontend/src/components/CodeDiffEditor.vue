<template>
  <div>
    <div id="code-diff-editor" style="width:100%;height:100%;border:1px solid grey"></div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor'

export default {
  name: 'codeDiffEditor',
  model: {
    prop: 'content',
    event: 'change'
  },
  props: {
    'content': null,
    'diffContent': null,
    'language': {
      default: 'javascript'
    },
    'readOnly': {
      default: false
    }
  },
  data: function () {
    return {
      editor: null,
      jsonPath: null
    }
  },
  watch: {
    content: function () {
      console.debug("Code diff editor: content change");
      if ((this.editor)) {
        this.editor.setModel({
        original: monaco.editor.createModel(this.content,this.language),
        modified: monaco.editor.createModel(this.diffContent,this.language)
        });
      }
    }
  },
  mounted: function () {
    const copyToClipboard = this.copyToClipboard
    this.editor = monaco.editor.createDiffEditor(
      this.$el.querySelector('#code-diff-editor'),
      {
        readOnly: this.readOnly,
        automaticLayout: true
      }
    )
    this.editor.setModel({
        original: monaco.editor.createModel(this.content,this.language),
        modified: monaco.editor.createModel(this.diffContent,this.language)
        });
    this.editor.addAction({
      id: 'json-path',
      label: 'Copy JsonPath',
      keybindings: [
        monaco.KeyMod.chord(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_J)
      ],
      precondition: "editorLangId == 'json'",
      keybindingContext: "editorLangId == 'json'",
      contextMenuGroupId: '9_cutcopypaste',
      contextMenuOrder: 2,
      run: copyToClipboard
    });
  },
  methods: {
    copyToClipboard () {
      const notification = this.$Notice
      if (this.jsonPath) {
        navigator.clipboard.writeText(this.jsonPath)
          .then(function () { }, function () {
            notification.error({
              title: 'jsonpath copy failed.'
            });
          }
          );
      } else {
        notification.warning({
          title: 'There is no jsonpath that can be copied.'
        });
      }
    }
  }
};
</script>
