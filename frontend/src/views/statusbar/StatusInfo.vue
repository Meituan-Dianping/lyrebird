<template>
  <span>
      <Poptip
        content="content"
        placement="top-start"
        class="main-footer-status"
        width="250"
      >
        <b class="main-footer-status-button">Bandwidth: {{bandwidthExplanation}} </b>
        <div slot="title">
          <b>Bandwidth</b>
        </div>
        <div slot="content">
          <Row type="flex" justify="space-around">
            <Col span="12" v-for="(item, index) in bandwidthTemplates" :key="index">
              <Button
                style="min-width:95px;margin-top:5px;"
                :class="item.bandwidth == bandwidth ? 'bandwidth-btn-highlight' : ''"
                @click.prevent="updateBandwidth(item.template_name)"
              >{{ item.template_name }}</Button>
            </Col>
          </Row>
        </div>
      </Poptip>
      <Poptip
        v-if="status"
        content="content"
        placement="top-end"
        class="main-footer-status"
        width="250"
      >
        <span class="main-footer-status-button">
          <Icon type="ios-arrow-up" style="padding-right:3px;"/>
          <b>Version {{status.version}}</b>
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
    this.$store.dispatch('loadBandwidth')
    this.$store.dispatch('loadBandwidthTemplates')
  },
  methods: {
    updateBandwidth (template_name) {
      this.$store.dispatch('updateBandwidth', template_name)
    }
  },
  computed: {
    status () {
      return this.$store.state.status
    },
    bandwidth () {
      return this.$store.state.bandwidth.bandwidth
    },
    bandwidthTemplates () {
      return this.$store.state.bandwidth.bandwidthTemplates
    },
    bandwidthExplanation () {
      for (let v of this.bandwidthTemplates) {
        if (this.bandwidth == v['bandwidth']) {
          if (this.bandwidth == -1) {
            return v['template_name']
          }
          else {
            return `${v['template_name']} ( ${v['bandwidth']} Kb/s)`
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.bandwidth-btn-highlight {
  background-color: #0fccbf !important;
  color: #fff;
  outline: none;
}
</style>
