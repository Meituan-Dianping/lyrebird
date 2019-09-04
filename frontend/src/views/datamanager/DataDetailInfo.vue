<template>
  <Row type="flex" justify="center" align="middle" @mouseover.native="isMouseOver=true" @mouseout.native="isMouseOver=false" style="margin-bottom:10px;word-break:break-all;">
    <Col span="5" align="right" style="padding:0px 10px 0px 0px">
      <Tooltip :content="deletable ? 'Delete': 'Undeletable key'" :delay="500" placement="bottom-start">
        <Icon 
          type="md-remove-circle" 
          :class="buttonClass" 
          v-show="isMouseOver" 
          @click.native="deleteInfoKey" 
          style="padding:0px 10px"
        />
      </Tooltip>
      <span>{{infoKey}}</span>
    </Col>
    <Col span="19" style="padding:0px 0px 0px 10px">
      <Input v-if="editable" v-model="inputvalue" type="textarea" :autosize="{ minRows: 1 }" size="small"/>
      <span v-else>{{infoValue}}</span>
    </Col>
  </Row>
</template>

<script>
export default {
  props: ['infoValue', 'infoKey', 'editable', 'deletable'],
  data() {
    return {
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
      }
    },
    buttonClass() {
      if (this.deletable) {
        return ['enable-button']
      } else {
        return ['disable-button']
      }
    }
  },
  methods: {
    deleteInfoKey() {
      if (this.deletable) {
        this.$store.commit('deleteGroupDetailItem', this.infoKey)
      }
    }
  }
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
