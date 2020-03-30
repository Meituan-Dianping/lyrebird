<template>
  <div style='padding:20px;'>
    <h1 style='text-align:center;margin-bottom:40px'>Lyrebird plugin demo</h1>

    <Row>
      <i-col span='12'>
        <h2 >mock list of the last 10</h2>
        <Table style="margin:10px 0;" border :columns="columns" :data="requestList"></Table>
      </i-col>
      <i-col span='12'>
        <div style='margin:0 50px ;'>
          <h2>remock</h2>
          <Input style='margin:10px 0;' v-model='remockPath'   @keyup.native.enter='remock'/>
          <h2>reset</h2>
          <Button style='margin:10px 0;' type='primary' @click='reset'>reset</Button>
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
    remock () {
      apis.remock(this.remockPath).then(response => {})
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
      remockPath:'http://www.baidu.com',
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
                    window.open('http://127.0.0.1:9090/api/flow/'+params.row.id,'_blank')
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
