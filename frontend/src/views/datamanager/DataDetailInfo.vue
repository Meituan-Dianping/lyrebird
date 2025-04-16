<template>
  <v-hover v-slot="{ hover: isMouseOver }">
    <v-row
      no-gutters
      align="start"
      style="word-break:break-all;"
      class="data-detail-info mb-3"
    >
      <v-col cols=2 class="pr-2">
        <p class="text-right ma-0">
          <v-btn
            icon
            v-show="isMouseOver"
            @click.stop="deleteInfoKey"
            :disabled="!deletable"
            title="Delete"
          >
            <v-icon size="12px" color="primary">mdi-minus-circle</v-icon>
          </v-btn>
          {{infoKey}}
        </p>
      </v-col>

      <v-col cols=10 class="pl-2">
        <span v-if="inputValueType === 'label'">
          <LabelDropdown :initLabels="infoValue" :placement="'bottom-start'" @onLabelChange="editLabel">
            <template #dropdownButton>
              <span v-for="(label, index) in infoValue">
                <span class="data-label" :style="'background-color:'+(label.color?label.color:'#808695')">{{label.name}}</span>
              </span>
              <v-btn icon class="ml-1"  title="Edit">
                <v-icon size="12px" color="primary">mdi-pencil</v-icon>
              </v-btn>
            </template>
          </LabelDropdown>
        </span>
        <span v-if="inputValueType === 'link'">
          <a :href=infoValue.link target="_blank"> {{ infoValue.link }}</a>
        </span>
        <span v-else-if="inputValueType === 'category'">
          <Select v-model="infoValue.selected" multiple size="small">
            <Option v-for="item in infoValue.allItem" :value="item.value" :key="item.value">{{ item.value }}</Option>
          </Select>
        </span>
        <span v-else-if="inputValueType === 'select'">
          <Select v-model="infoValue.value" size="small">
            <Option v-for="item in infoValue.items" :value="item.value" :key="item.value" class="data-detail-info-select-option">{{ item.label }}</Option>
          </Select>
        </span>
        <span v-else-if="inputValueType === 'longList'">
          <div class="row no-gutters mb-1" v-for="listItem in longListValue">
            <div class="col-5">
              <span>{{listItem.id}}</span>
            </div>
            <div class="col-7 text-truncate">
              <span>{{listItem.name}}</span>
            </div>
          </div>
          <v-btn v-show="infoValue.length > longListShowLessCount" plain class="px-0" height="20" color="primary" @click="changeTextLongListShowAll">
            <span>{{isLongListShowAll ? 'Show Less': 'Show More'}}</span>
          </v-btn>
        </span>
        <span v-else-if="inputValueType === 'stringObject'">
          <v-row no-gutters>

            <v-textarea
              v-if="editable"
              class="data-detail-info-input shading"
              outlined
              dense
              v-model="infoValue.value"
              hide-details
              rows=1
              auto-grow
              background-color="#ffffff"
            />
            <span v-else>
              {{infoValue.value}}
            </span>

            <v-btn v-show="isDisplayCopyIcon" icon x-small title='Copy'>
              <v-icon
                x-small
                color="context"
                v-clipboard:copy="inputValue"
                v-clipboard:success="onUrlCopy"
                v-clipboard:error="onUrlCopyError"
              >{{copyIcon}}</v-icon>
            </v-btn>

            <v-menu offset-y open-on-hover :close-on-content-click="false">
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  plain
                  icon
                  small
                  v-show="infoValue.info"
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon small size="18px" color="content">mdi-information-outline</v-icon>
                </v-btn>
              </template>
              <div class="data-detail-info-string-object-info-menu pa-2">
                {{infoValue.info}}
              </div>
            </v-menu>

            <span v-show="isDisplayPoptipIcon">
              <v-menu offset-y offset-overflow class="pt-2" :value="isDisplayPoptip">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn plain icon v-bind="attrs" v-on="on" @click="showQrcode">
                    <v-icon color="content">mdi-qrcode</v-icon>
                  </v-btn>
                </template>
                <div class="data-detail-info-string-qrcode pa-2">
                  <vue-qr :text="qrcodeText" :margin=4 :size="getQrcodeImgWidth()" />
                </div>
              </v-menu>
            </span>

          </v-row>
        </span>
        <span v-else-if="inputValueType === 'string'">
          <v-row no-gutters>
            <v-textarea
              v-if="editable"
              class="data-detail-info-input shading"
              outlined
              dense
              v-model="inputValue"
              hide-details
              rows=1
              auto-grow
              background-color="#ffffff"
            />
            <span v-else>
              {{inputValue}}
            </span>

            <span v-show="isDisplayPoptipIcon" class="pl-2">
              <v-menu offset-y offset-overflow class="pt-2" :value="isDisplayPoptip">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn plain icon v-bind="attrs" v-on="on" @click="showQrcode">
                    <v-icon color="content">mdi-qrcode</v-icon>
                  </v-btn>
                </template>
                <div class="data-detail-info-string-qrcode pa-2">
                  <vue-qr :text="qrcodeText" :margin=4 :size="getQrcodeImgWidth()" />
                </div>
              </v-menu>
            </span>

            <v-btn v-show="isDisplayCopyIcon" icon x-small title='Copy'>
              <v-icon
                x-small
                color="context"
                v-clipboard:copy="inputValue"
                v-clipboard:success="onUrlCopy"
                v-clipboard:error="onUrlCopyError"
              >{{copyIcon}}</v-icon>
            </v-btn>
          </v-row>
        </span>
      </v-col>
    </v-row>
  </v-hover>


</template>

<script>
import svgIcon from 'vue-svg-icon/Icon.vue'
import { render } from '@/api'
import LabelDropdown from '@/components/LabelDropdown.vue'
import VueQr from 'vue-qr'
import { parse, stringify } from 'lossless-json'

export default {
  props: ['infoKey', 'editable', 'deletable'],
  components: {
    svgIcon,
    LabelDropdown,
    VueQr
  },
  data() {
    return {
      qrcodeText: '',
      imgData: '',
      isDisplayPoptip: false,
      isLongListShowAll: false,
      longListShowLessCount: 5,
      copyIcon: 'mdi-content-copy'
    }
  },
  computed: {
    inputValue: {
      get () {
        let infoValue = this.$store.state.dataManager.groupDetail[this.infoKey]
        if (infoValue === null) {
          return infoValue
        } else if (this.inputValueType === 'stringObject') {
          return infoValue.value
        } else if (typeof infoValue === 'object') {
          return stringify(infoValue)
        } else {
          return infoValue
        }
      },
      set (val) {
        this.$store.commit('setGroupDetailItem', { key: this.infoKey, value: val })
      }
    },
    infoValue () {
      return this.$store.state.dataManager.groupDetail[this.infoKey]
    },
    longListValue () {
      if (this.isLongListShowAll) {
        return this.infoValue
      }
      return this.infoValue.slice(0, this.longListShowLessCount)
    },
    isDisplayCopyIcon () {
      return this.$store.state.dataManager.displayCopyKey.indexOf(this.infoKey) !== -1
    },
    isDisplayPoptipIcon () {
      if (!String(this.inputValue).match('(?=.*://)')) {
        return false
      }
      if (this.$store.state.snapshot.groupDetailDisplayKey === this.infoKey ) {
        this.isDisplayPoptip = true
        this.$store.commit('clearGroupDetailDisplayKey')
        this.showQrcode ()
      }
      return true
    },
    inputValueType () {
      if (this.infoKey === 'label') {
        return 'label'
      } else if (this.infoKey === 'category') {
        return 'category'
      } else if (this.infoKey === 'super_by') {
        return 'longList'
      } else if (this.infoValue && this.infoValue.hasOwnProperty('items') && this.infoValue.hasOwnProperty('value')) {
        return 'select'
      } else if (this.infoValue && this.infoValue.hasOwnProperty('value') && this.infoValue.hasOwnProperty('info') ) {
        return 'stringObject'
      } else if (this.infoValue && this.infoValue.hasOwnProperty('link') && this.infoValue.hasOwnProperty('value') ) {
        return 'link'
      } else {
        return 'string'
      }
    }
  },
  methods: {
    deleteInfoKey() {
      if (this.deletable) {
        this.$store.commit('deleteGroupDetailItem', this.infoKey)
      }
    },
    editLabel (payload) {
      let labels = this.$store.state.dataManager.groupDetail[this.infoKey]
      // Value of manually entered label is empty string
      if (labels === null || labels === '') {
        this.$store.state.dataManager.groupDetail[this.infoKey] = []
        labels = this.$store.state.dataManager.groupDetail[this.infoKey]
      }
      if (payload.action === 'add') {
        let labelInfo = this.$store.state.dataManager.labels[payload.id]
        labels.push({
          name: labelInfo.name,
          color: labelInfo.color,
          description: labelInfo.description
        })
      } else if (payload.action === 'remove') {
        let target = ''
        for (const index in labels) {
          if (labels[index].name === payload.name) {
            target = index
            break
          }
        }
        labels.splice(target, 1)
      } else { }
      this.$store.commit('setGroupDetailItem', { key: this.infoKey, value: labels })
      this.$store.dispatch('loadDataLabel')
    },
    showQrcode () {
      let node = {}
      Object.assign(node, this.$store.state.dataManager.focusNodeInfo)
      node.info = {}
      node.info[this.infoKey] = this.infoValue
      this.$store.dispatch('activateGroup', node)

      render(this.inputValue)
        .then(response => {
          this.qrcodeText = response.data.data
        })
        .catch(error => {
          this.$bus.$emit('msg.error', 'Render text error: ' + error.data.message)
        })
    },
    getQrcodeImgWidth () {
      if (!this.inputValue) {
        return 0
      } else if (this.inputValue.length < 100) {
        return 150
      } else if (this.inputValue.length < 1024) {
        return 250
      } else {
        return 382
      }
    },
    changeTextLongListShowAll () {
      this.isLongListShowAll = !this.isLongListShowAll
    },
    onUrlCopy () {
      const originCopyIcon = this.copyIcon
      this.copyIcon = 'mdi-check'
      setTimeout(() => {
        this.copyIcon = originCopyIcon
      }, 2 * 1000)
    },
    onUrlCopyError (e) {
      this.$bus.$emit('msg.error', 'Copy url error:' + e)
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
.data-label {
  font-size: 12px;
  padding: 0px 6px;
  margin: 0px 3px;
  color:white;
  border-radius: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  max-width: 200px;
  vertical-align: bottom;
  font-weight: 500;
}
.data-detail-info-string-object-info-menu {
  background-color: #fff;
  min-width: 200px;
  max-width: 600px;
}
.data-detail-info-string-qrcode {
  background-color: #fff;
}
.data-detail-info .v-btn--icon.v-size--default {
  height: 18px;
  width: 18px;
}
.data-detail-info-input {
  font-size: 14px;
}
.data-detail-info-input .v-input__slot {
  min-height: 24px !important;
  padding: 0px 4px !important;
}
.data-detail-info-input textarea {
  color: #515a6e !important;
  line-height: 20px !important;
  min-height: 24px !important;
  margin-top: 2px !important;
}
</style>
