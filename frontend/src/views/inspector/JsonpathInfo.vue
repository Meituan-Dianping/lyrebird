<template>
  <v-menu
    v-if="jsonpath"
    :close-on-content-click="false"
    offset-y
    open-on-hover
  >
    <template v-slot:activator="{ on, attrs }">

      <span v-bind="attrs" v-on="on" class="jsonpath-menu">
        <v-btn icon x-small plain title='Copy'>
          <v-icon
            x-small
            color="context"
            v-clipboard:copy="jsonpath"
            v-clipboard:success="onUrlCopy"
            v-clipboard:error="onUrlCopyError"
          >{{copyIcon}}</v-icon>
        </v-btn>
        <b>JSONPath:</b>
        <span class="pl-1">{{jsonpath}}</span>
      </span>
    </template>
    <div class="jsonpath-info pa-2">
      {{jsonpath}}
    </div>
  </v-menu>

</template>

<script>
export default {
  props: ['jsonpath'],
  data () {
    return {
      copyIcon: 'mdi-content-copy'
    }
  },
  methods: {
    onUrlCopy () {
      const originCopyIcon = this.copyIcon
      this.copyIcon = 'mdi-check'
      setTimeout(() => {
        this.copyIcon = originCopyIcon
      }, 2 * 1000)
    },
    onUrlCopyError (e) {
      this.$bus.$emit('msg.error', 'Copy url error:' + e)
    }
  }
}
</script>

<style scoped>
.jsonpath-info {
  background-color: #fff;
  min-width: 200px;
  max-width: 400px;
  word-break: break-all;
}
.jsonpath-menu{
  display: inline-block;
  width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
