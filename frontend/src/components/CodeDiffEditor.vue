<template>
  <div>
    <div id="code-diff-editor" class="pa-3" style="width:100%;height:100%;border-top:1px solid grey"></div>
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
      editor: null
    }
  },
  watch: {
    diffContent: function () {
      console.debug("Code diff editor: content change");
      if (this.editor) {
        this.editor.setModel({
        original: monaco.editor.createModel(this.content, this.language),
        modified: monaco.editor.createModel(this.diffContent, this.language)
        });
      }

      const modifiedEditor = this.editor.getModifiedEditor()
      modifiedEditor.getAction('editor.action.formatDocument').run()

      // The condition of formatDocument is that the diff content is not read-only, and formatDocument is async.
      // So add 1 second delay to wait for the formatting to complete, and then set the diff content to read-only.
      setTimeout(() => {
        modifiedEditor.updateOptions({
          readOnly: true
        })
      }, 1000)
    }
  },
  mounted: function () {
    this.editor = monaco.editor.createDiffEditor(
      this.$el.querySelector('#code-diff-editor'),
      {
        readOnly: this.readOnly,
        automaticLayout: true
      }
    )
    this.editor.setModel({
      original: monaco.editor.createModel(this.content, this.language),
      modified: monaco.editor.createModel(this.diffContent, this.language)
    })
  }
};
</script>
