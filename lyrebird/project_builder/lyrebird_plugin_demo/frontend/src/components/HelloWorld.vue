<template>
  <div>
    <h2>Lyrebird plugin demo</h2>
    <div>
      Send request to lyrebird use
      <br />
      <code>curl http://localhost:9090/mock/http://www.google.com</code>
      <br />Then you can get requests info by click "Count" button.
    </div>
    <Divider />
    <div>
      <label>
        <b>Count</b>
      </label>
      {{count}}
    </div>
    <div>
      <label>
        <b>Last URL</b>
      </label>
      {{lastURL}}
    </div>
    <Divider />
    <div>
      <Button @click="load">Reload</Button>
      <Button @click="reset">Reset</Button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  methods: {
    load () {
      this.$store.dispatch('reloadReqestCount')
    },
    reset () {
      this.$store.dispatch('resetRequestCount')
    }
  },
  computed: {
    count () {
      return this.$store.state.requestCount
    },
    lastURL () {
      return this.$store.state.lastRequestURL
    }
  }
}
</script>
