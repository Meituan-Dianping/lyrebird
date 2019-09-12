<template>
  <div v-if="checkerDetail">
    <code-editor :language="codeType" :content="checkerDetail" class="checker-detail"></code-editor>
  </div>
  <div v-else class="checker-empty">
    No selected script
  </div>
</template>

<script>
import CodeEditor from '@/components/CodeEditor.vue'

  export default {
    components:{
      CodeEditor
    },
    data () {
      return {
        codeType: 'python'
      }
    },
    computed: {
      checkerDetail() {
        return this.$store.state.checker.focusCheckerDetail
      }
    }
  }
</script>

<style>
  .checker-detail {
    height: calc(100vh - 68px);
    /* total:100vh
    header: 38px
    border: 1px
    editor
    border: 1px
    footer: 28px
    */
  }
</style>
