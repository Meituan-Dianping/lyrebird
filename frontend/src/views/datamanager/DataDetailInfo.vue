<template>
  <div>
    <Row v-for="(value, key) in displayInformation" :key="key" style="padding-top:10px">
      <Col span="5" offset="1">
        <span>{{key}}</span>
      </Col>
      <Col span="18">
        <Input v-if="readOnly.indexOf(key) === -1" v-model="displayInformation[key]" :placeholder="value" size="small" />
        <span v-else>{{value}}</span>
      </Col>
    </Row>
  </div>
</template>

<script>
export default {
  props: ['information'],
  data() {
    return {
      unshowInfoKey: ['children', 'type', 'parent_id'],
      readOnly: ['id', 'rule']
    }
  },
  computed: {
    displayInformation() {
      let res = {}
      for (const key in this.information) {
        if (this.unshowInfoKey.indexOf(key) === -1 && key.substring(0,1) !== '_') {
          res[key] = this.information[key]
        }
      }
      return res
    }
  }
}
</script>
