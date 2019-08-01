<template>
  <Row type="flex" justify="center" align="middle" @mouseover.native="isMouseOver=true" @mouseout.native="isMouseOver=false" style="margin-bottom:10px;word-break:break-all;">
    <Col span="6" align="right" style="padding:0px 10px">
      <Tooltip :content="this.readOnly.indexOf(this.infoKey)===-1 ? 'Delete': 'Undeletable key'" :delay="500">
        <Icon type="md-remove-circle" :class="buttonClass" v-show="isMouseOver" @click.native="deleteInfoKey" style="padding:0px 10px"/>
      </Tooltip>
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
      readOnly: ['id', 'rule', 'secondary_search_id'],
      isMouseOver: false
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
    },
    buttonClass() {
      if (this.readOnly.indexOf(this.infoKey) === -1) {
        return ['enable-button']
      } else {
        return ['disable-button']
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
.enable-button {
  cursor: pointer;
}
.disable-button {
  color: #c5c8ce;
}
</style>
