<template>
  <div>
    <div id="code-diff-editor" style="width:100%;height:100%;border:1px solid grey"></div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor'
import { getJsonPath } from './jsonpath'

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
      console.debug("Code editor: content change");
      if ((this.editor)) {
        this.editor.setModel({
        language: this.language,
        theme: 'vs',
        // 展示response
        original: monaco.editor.createModel(this.content),
        // 展示proxy response
        modified: monaco.editor.createModel(this.diffContent)
        });
      }
    }
  },
  mounted: function () {
    const copyToClipboard = this.copyToClipboard
    // this.editor.dispose();
    this.editor = monaco.editor.createDiffEditor(
      this.$el.querySelector('#code-diff-editor'),
      {
        language: this.language,
        theme: 'vs',
        readOnly: this.readOnly,
        automaticLayout: true
      }
    )
    this.editor.setModel({
        language: this.language,
        theme: 'vs',
        // 展示response
        original: monaco.editor.createModel(this.content),
        // 展示proxy response
        modified: monaco.editor.createModel(this.diffContent)
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
    // this.editor.onDidChangeModelContent(event => {
    //   const value = this.editor.getValue()
    //   if (this.value !== value) {
    //     this.$emit('change', value, event)
    //   }
    // })
    // this.editor.onDidChangeCursorPosition(event => {
    //   const value = this.editor.getValue()
    //   const offSet = this.editor.getModel().getOffsetAt(event.position)
    //   const language = this.language;
    //   if (this.value !== value && language === 'json') {
    //     this.$emit('on-cursor-change', { offSet: offSet })
    //   }
    //   if (language == 'json' && offSet !== 0) {
    //     this.jsonPath = getJsonPath(value, offSet)
    //     this.$emit('on-jsonpath-change', { jsonPath: this.jsonPath })
    //   }
    // })
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
