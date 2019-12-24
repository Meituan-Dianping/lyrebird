<template>
  <Row type="flex" align="middle" @mouseover.native="isMouseOver=true" @mouseout.native="isMouseOver=false" style="margin-bottom:10px;word-break:break-all;">
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
      <span v-if="inputValueType === 'link'">
        <Input v-model="inputValue" type="textarea" :autosize="{ minRows: 1 }" size="small" style="width:calc(100% - 30px);"/>
        <Poptip placement="bottom" width="382" word-wrap @on-popper-show="loadQrcodeImg">
          <svg-icon class="ivu-icon" name="qrcode" scale="2.8" style="margin-left:3px;cursor: pointer;"/>
          <div slot="content">
            <img :src="imgData" style="width:100%">
          </div>
        </Poptip>
      </span>
      <span v-else-if="inputValueType === 'input'">
        <Input v-model="inputValue" type="textarea" :autosize="{ minRows: 1 }" size="small"/>
      </span>
      <span v-else>
        {{inputValue}}
      </span>
    </Col>
  </Row>
</template>

<script>
import svgIcon from 'vue-svg-icon/Icon.vue'
import { getQrcodeImg } from '@/api'

export default {
  props: ['infoKey', 'editable', 'deletable'],
  components: {
    svgIcon
  },
  data() {
    return {
      imgData: '',
      isMouseOver: false
    }
  },
  computed: {
    inputValue: {
      get () {
        let infoValue = this.$store.state.dataManager.groupDetail[this.infoKey]
        if (infoValue === null) {
          return infoValue
        } else if (typeof infoValue === 'object') {
          return JSON.stringify(infoValue)
        } else {
          return infoValue
        }
      },
      set (val) {
        this.$store.commit('setGroupDetailItem', { key: this.infoKey, value: val })
      }
    },
    buttonClass () {
      if (this.deletable) {
        return ['enable-button']
      } else {
        return ['disable-button']
      }
    },
    inputValueType () {
      if (String(this.inputValue).match('(?=.*://)')) {
        return 'link'
      } else if (this.editable) {
        return 'input'
      } else {
        return 'text'
      }
    }
  },
  methods: {
    deleteInfoKey() {
      if (this.deletable) {
        this.$store.commit('deleteGroupDetailItem', this.infoKey)
      }
    },
    loadQrcodeImg () {
      this.$store.dispatch('activateGroup', this.$store.state.dataManager.focusNodeInfo)
      this.imgData = ''
      getQrcodeImg(this.inputValue)
        .then(response => {
          this.imgData = response.data.img
        })
        .catch(error => {
          this.$bus.$emit('msg.error', 'Make QRCode error: ' + error)
        })
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
