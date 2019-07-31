<template>
  <Row type="flex" justify="center" align="middle" style="margin-bottom:10px;word-break:break-all;">
    <Col span="1" align="right" style="padding:0px 10px">
      <Icon type="md-remove-circle" class="delete-button" v-show="readOnly.indexOf(this.infoKey) === -1" @click.native="deleteInfoKey"/>
    </Col>
    <Col span="5" align="right" style="padding:0px 10px">
      <span>{{this.infoKey}}</span>
    </Col>
    <Col span="18" style="padding:0px 0px 0px 10px">
      <span v-if="readOnly.indexOf(this.infoKey) > -1">{{this.infoValue}}</span>
      <Input v-else v-model="inputvalue" type="textarea" :autosize="{ minRows: 1 }" size="small"/>
    </Col>
  </Row>
</template>

<script>
export default {
  props: ['infoValue', 'infoKey'],
  data() {
    return {
      readOnly: ['id', 'rule', 'secondary_search_id']
    }
  },
  computed: {
    inputvalue: {
      get () {
        return this.$store.state.dataManager.groupDetail[this.infoKey]
      },
      set (val) {
        this.$store.commit('setGroupDetailItem', { key: this.infoKey, value: val })
        this.$store.commit('setIsGroupDetailChanged', true)
      }
    }
  },
  methods: {
    deleteInfoKey() {
      this.$store.commit('deleteGroupDetailItem', this.infoKey)
      this.$store.commit('setIsGroupDetailChanged', true)
    }
  },
}
</script>

<style>
.delete-button {
  cursor: pointer;
}
</style>
