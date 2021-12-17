<template>
  <div v-if="checkerDetail">
    <code-editor :language="codeType" v-model="checkerDetail" class="checker-detail"></code-editor>
    <div class="save-btn" v-if="checkerDetail">
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
  <div v-else class="checker-empty">
    No selected script
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
  mounted () {
  this.$bus.$on('keydown', this.onKeyDown)
  },
  beforeDestroy () {
    this.$bus.$off('keydown', this.onKeyDown)
  },
  computed: {
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
      if (this.checkerDetail) {
        this.saveCheckerDetail()
      }
      event.preventDefault()
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
  .save-btn {
    color: #fff;
    font-size: 0.6rem;
    text-align: center;
    line-height: 3rem;
    width: 3rem;
    height: 3rem;
    position: fixed;
    right: 60px;
    bottom: 60px;
    border-radius: 50%;
    z-index: 500;
  }
  .save-btn-detail {
    width: 36px !important;
    height: 36px !important;
  }
  .save-btn-icon {
    font-size: 20px !important;
    width: 20px !important;
    height: 20px !important;
  }
</style>
