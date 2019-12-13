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
        <Poptip placement="bottom" width="382" word-wrap @on-popper-show="qrcodeRemake">
          <svg-icon class="ivu-icon" name="qrcode" scale="2.8" style="margin-left:3px;cursor: pointer;"/>
          <div slot="content">
            <div id="qrcodeobj" ref="qrcodeobj"/>
          </div>
        </Poptip>
      </span>
      <span v-else-if="inputValueType === 'input'">
        <Input v-model="inputValue" type="textarea" :autosize="{ minRows: 1 }" size="small"/>
      </span>
      <span v-else>
        {{infoValue}}
      </span>
    </Col>
  </Row>
</template>

<script>
import QRCode from 'qrcodejs2'
import svgIcon from 'vue-svg-icon/Icon.vue'

export default {
  props: ['infoValue', 'infoKey', 'editable', 'deletable'],
  components: {
    svgIcon
  },
  data() {
    return {
      qrcodeObj: '',
      maxLengthDisplayQrcode: 1270,
      isMouseOver: false
    }
  },
  mounted () {
    if (this.inputValueType === 'link') {
      this.qrcodeMethod()
    }
  },
  computed: {
    inputValue: {
      get () {
        return this.$store.state.dataManager.groupDetail[this.infoKey]
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
      if (String(this.infoValue).match('(?=.*://)')) {
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
    qrcodeMethod () {
      this.qrcodeObj = new QRCode(this.$refs.qrcodeobj, {
        width: 350,
        height: 350,
        text: this.inputValue,
        correctLevel : QRCode.CorrectLevel.H
      })
    },
    qrcodeRemake () {
      if (this.infoValue.length > this.maxLengthDisplayQrcode) {
        this.$bus.$emit('msg.error', 'Make qrcode failed: ' + this.maxLengthDisplayQrcode + ' character is allowed, current length is ' + this.infoValue.length)
      } else {
        this.qrcodeObj.makeCode(this.inputValue)
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
