<template>
  <div style="padding:20px;" id="main">
    <h1 style="text-align:center;margin-bottom:40px">Lyrebird plugin demo</h1>

    <Row>
      <i-col span="12">
        <Row>
          <i-col span="3">
            <Button type="primary" @click="reset">Clear</Button>
          </i-col>
          <i-col span="21">
            <i-input class="active" v-model="mockPath" @keyup.enter.native="mock">
              <Icon type="ios-search" slot="suffix" color="blue" @click="mock" />
            </i-input>
          </i-col>
        </Row>

        <Table style="margin:10px 0;" border :columns="columns" :data="requestList"></Table>
      </i-col>
      <i-col span="12">
        <div style="margin:0 50px ;">
          <h2>🚀 PROXY / MOCK</h2>
          <div style="margin:10px;">
            <span style="font-size:18px;">
              Input domain and click search icon or keyup enter.
              <br />
            </span>
            <span style="font-size:18px;">
              You will proxy or mock the domain by lyrebird
              <br />
            </span>
          </div>
          <br />
          <h2>✈️API</h2>
          <div style="margin:10px;">
            <span style="font-size:18px;">You can define API in manifest.py</span>
            <br />
            <span style="font-size:18px;">
              Learn more lyrebird core API from here:
              <a
                href="https://meituan-dianping.github.io/lyrebird/guide/api.html"
                target="_blank"
              >API DOC</a>
            </span>
          </div>
          <br />
          <h2>🚢EVENT</h2>
          <div style="margin:10px;">
            <span style="font-size:18px;">
              You can define event in manifest.py,
              and you will get some message from lyrebird async channel
            </span>
          </div>
          <br />
          <h2>🚗BACKGROUND</h2>
          <div style="margin:10px;">
            <span style="font-size:18px;">
              You can define background task in manifest.py.
              It will influence lyrebird performance, is not recommend to use.
            </span>
          </div>
          <br />
          <h2>🚴‍♀️STATUS BAR</h2>
          <div style="margin:10px;">
            <span style="font-size:18px;">
              You can define status bar in manifest.py.
              It will set a plugin (Image or Text) in footbar, like the demo : lyrebird_qacode plugin
            </span>
          </div>
          <br />
          <h2>🚚MORE PLUGINS</h2>
          <div style="margin:10px;">
            <span style="font-size:18px;">
              You can find more open source lyrebird plugins from here :
              <a
                href="https://meituan-dianping.github.io/lyrebird/plugins/"
                target="_blank"
              >Plugins.</a>
              We are looking forward more friends to develop and open source your lyrebird plugin
            </span>
          </div>
          <br />
        </div>
      </i-col>
    </Row>
  </div>
</template>

<script>
import * as apis from '../apis'

export default {
  name: 'HelloWorld',
  created () {
    this.load()
    this.$io.on('loadRequestList', this.load)
  },
  methods: {
    load () {
      this.$store.dispatch('reloadReqestList')
    },
    reset () {
      this.$store.dispatch('resetRequestReset')
      this.$store.dispatch('reloadReqestList')
    },
    mock () {
      apis.mock(this.mockPath).then(response => {})
    }
  },
  computed: {
    requestList () {
      return this.$store.state.requestList
    },
    lastURL () {
      return this.$store.state.lastRequestURL
    }
  },
  data () {
    return {
      mockPath: 'http://www.baidu.com',
      columns: [
        {
          title: 'Data ID',
          key: 'id',

        },
        {
          title: 'uri',
          key: 'uri'
        },
        {
          title: 'Action',
          key: 'action',
          width: 150,
          align: 'center',
          render: (h, params) => {
            return h('div', [
              h('Button', {
                props: {
                  type: 'primary',
                  size: 'small'
                },
                style: {
                  marginRight: '5px'
                },
                on: {
                  click: () => {
                    window.open('http://127.0.0.1:9090/api/flow/' + params.row.id, '_blank')
                  }
                }
              }, 'View')
            ])
          }
        }
      ]
    }
  }
}
</script>
<style  scoped>
#main {
  min-width: 1200px;
}
</style>>

