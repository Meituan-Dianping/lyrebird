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
          <Row v-for="key in showedStatus" :key="key">
            <i-col span="11">
              <b style="float: right">{{key.toUpperCase()}}</b>
            </i-col>
            <i-col span="12" offset="1">{{status[key]}}</i-col>
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
  </span>
</template>

<script>

export default {
  data () {
    return {
        showedStatus: ["ip", "mock.port", "proxy.port"]
    }
  },
  mounted () {
    this.$store.dispatch('loadStatus')
  },
  methods: {
  },
  computed: {
    status () {
      return this.$store.state.status
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
