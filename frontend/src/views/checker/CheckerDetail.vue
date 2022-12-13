<template>
  <div v-if="focusChecker.length > 0">
    <code-editor :language="codeType" v-model="checkerDetail" class="checker-detail"></code-editor>
    <div class="save-btn" v-if="focusChecker">
      <v-tooltip top>
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            v-bind="attrs"
            v-on="on"
            fab
            dark
            color="primary"
            class="save-btn-detail"
            @click="saveCheckerDetail"
          >
            <v-icon 
            class="save-btn-icon"
            dark>
              mdi-content-save-outline
            </v-icon>
          </v-btn>
        </template>
        <span>Save (⌘+s)</span>
      </v-tooltip>
    </div>
  </div>
  <div v-else class="extension-empty">
    <v-icon class="empty-icon" large>mdi-package-variant-closed</v-icon>
    <p class="empty-text">No Selected Script</p>
  </div>
</template>

<script>
import CodeEditor from '@/components/CodeEditor.vue'
import Icon from 'vue-svg-icon/Icon.vue'

export default {
  components:{
    CodeEditor,
    Icon
  },
  data () {
    return {
      codeType: 'python'
    }
  },
  activated () {
    this.$bus.$on('keydown', this.onKeyDown)
  },
  deactivated () {
    this.$bus.$off('keydown', this.onKeyDown)
  },
  computed: {
    focusChecker () {
      return this.$store.state.checker.focusChecker
    },
    checkerDetail: {
      get () {
        return this.$store.state.checker.focusCheckerDetail
      },
      set (val) {
        this.$store.commit('setFocusCheckerDetail', val)
      }
    }
  },
  methods: {
    saveCheckerDetail () {
      this.$store.dispatch('saveCheckerDetail')
    },
    onKeyDown (event) {
      if (event.code !== "KeyS" || !event.metaKey) {
        return
      }
      if (this.focusChecker) {
        this.saveCheckerDetail()
      }
      event.preventDefault()
    }
  }
}
</script>

<style>
  .checker-detail {
    height: calc(100vh - 44px - 40px - 28px - 12px);
    /* total:100vh
    header: 44px
    title: 40px
    editor
    margin-bottom: 12px
    footer: 28px
    */
  }
</style>
