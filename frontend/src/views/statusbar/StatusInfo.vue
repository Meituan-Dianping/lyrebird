<template>
  <span>
      <Poptip
        v-if="status"
        content="content"
        placement="top-end"
        class="main-footer-status"
        width="250"
      >
        <span class="main-footer-status-button">
          <Icon type="ios-arrow-up" style="padding-right:3px;"/>
          <b>Lyrebird {{status.version}}</b>
        </span>
        <div slot="title">
          <b>Lyrebird {{status.version}}</b>
        </div>
        <div slot="content">
          <Row>
            <i-col span="9">
              <b style="float: right">IP</b>
            </i-col>
            <i-col span="14" offset="1">
              {{status.ip}}
              <v-btn icon x-small @click.stop="showDialogChangeIp" title="Update info">
                <v-icon size="12px" color="primary">mdi-pencil</v-icon>
              </v-btn>
            </i-col>
          </Row>
          <Row v-for="key in showedStatus" :key="key">
            <i-col span="9">
              <b style="float: right">{{key.toUpperCase()}}</b>
            </i-col>
            <i-col span="14" offset="1">{{status[key]}}</i-col>
          </Row>
          <Divider style="margin:10px 0;"/>
          <div style="text-align:center">
            <strong>
              Copyright &copy; 2018-present 
              <a href="https://meituan-dianping.github.io/lyrebird" target="_blank" >Meituan</a>.
            </strong>
          </div>
        </div>
      </Poptip>
      <span class="main-footer-status">
        <a
          href="https://github.com/Meituan-Dianping/lyrebird/issues/new?assignees=&labels=&template=bug_report.md&title="
          target="_blank"
        >
          <v-icon size="16px" color="white">mdi-ladybug</v-icon> 
        </a>
      </span>
      <span class="main-footer-status-placeholder"></span>

      <DialogChangeIP/>

  </span>
</template>

<script>
import DialogChangeIP from '@/views/statusbar/DialogChangeIP.vue'

export default {
  components: {
    DialogChangeIP
  },
  data () {
    return {
      showedStatus: ['mock.port', 'proxy.port']
    }
  },
  mounted () {
    this.$store.dispatch('loadStatus')
  },
  computed: {
    status () {
      return this.$store.state.status
    }
  },
  methods: {
    showDialogChangeIp () {
      this.$store.commit('setIsShownDialogChangeIp', true)
    }
  }
}
</script>

<style scoped>
.bandwidth-btn-highlight {
  background-color: #5F5CCA !important;
  color: #fff;
  outline: none;
}
</style>
