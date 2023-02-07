<template>
  <div>
    <div id="code-diff-editor" style="width:100%;height:100%;padding:12px"></div>
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
      if ((this.editor)) {
        this.editor.setModel({
        original: monaco.editor.createModel(this.content,this.language),
        modified: monaco.editor.createModel(this.diffContent,this.language)
        });
      }
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
        original: monaco.editor.createModel(this.content,this.language),
        modified: monaco.editor.createModel(this.diffContent,this.language)
        });
  }
};
</script>
