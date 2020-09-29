<template>
  <div>
    <Dropdown
      trigger="click"
      :placement="placement?placement:'bottom-start'"
      @on-click="onDropdownMenuClick"
      transfer-class-name="label-dropdown"
      transfer
    >
      <slot name="dropdownButton" />
      <DropdownMenu slot="list">
        <p @click.stop>
          <Input v-model="searchStr" style="padding:8px 16px 8px;" size="small" placeholder="Label name"/>
        </p>
        <p v-if="labels.length === 0" style="text-align:center">No label</p>
        <div v-else style="min-width:250px;max-width:350px;">
          <DropdownItem
            v-for="label of labels"
            :key="label.id"
            align="left"
            :name="label.name"
            :selected="selectedLabel.includes(label.id)"
            style="padding: 8px 16px;"
          >
            <span
              class="data-label"
              :style="'padding:2px 6px;background-color:'+(label.color?label.color:'#808695')"
            >
              {{label.name}}
            </span>
            <span
              style="color:#808695;padding-left:10px;line-height:18px;"
            >
              {{label.description}}
            </span>
            <Icon
              v-show="selectedLabel.includes(label.id)"
              type="md-checkmark"
              size="14"
              color="rgba(45,140,240,0.9)"
              style="float:right;padding-left:10px;"
            />
          </DropdownItem>
        </div>
        <p style="padding:8px 16px 0px;font-size:12px;">
          <a v-if="selectedLabel.length" @click="clearSelectedLabels" style="font-size:12px;">
            Clear select labels
          </a>
          <a @click="changeLabelModalOpenState" style="float:right;font-size:12px;">
            Edit all labels
          </a>
        </p>
      </DropdownMenu>
    </Dropdown>
    <LabelEditor ref="labelModal"/>
  </div>  
</template>

<script>
import LabelEditor from '@/components/LabelModal.vue'

export default {
  props: ['initLabels', 'placement'],
  components: {
    LabelEditor
  },
  data () {
    return {
      searchStr: '',
      selectedLabel: [],
      labels: []
    }
  },
  created () {
    this.$store.dispatch('loadDataLabel')
    this.initSelectedLabel()
  },
  computed: {
    originLabelList () {
      return this.$store.state.dataManager.labels
    }
  },
  watch: {
    initLabels (val) {
      this.initSelectedLabel()
      this.refreshLabelList()
    },
    originLabelList () {
      this.refreshLabelList()
    },
    searchStr () {
      this.refreshLabelList()
    }
  },
  methods: {
    refreshLabelList () {
      this.labels = []
      for (const key in this.$store.state.dataManager.labels) {
        const label = this.$store.state.dataManager.labels[key]
        const name = label.name.toLowerCase()
        const searchStr = this.searchStr.toLowerCase()
        if (name.includes(searchStr)) {
          this.labels.push(label)
        }
      }
    },
    getLabelByName (name) {
      for (const key in this.$store.state.dataManager.labels) {
        const label = this.$store.state.dataManager.labels[key]
        if (label.name == name) {
          return label
        }
      }
    },
    initSelectedLabel () {
      this.selectedLabel = []
      this.searchStr = ''
      if (!this.initLabels || !this.initLabels.length) {
        return
      }
      console.log('this.initLabels', this.initLabels);
      for (const label of this.initLabels) {
        let target_label = this.getLabelByName(label.name)
        this.selectedLabel.push(target_label.id)
      }
    },
    onDropdownMenuClick (name) {
      let target_label = this.getLabelByName(name)
      let emitInfo = { name, id: target_label.id }

      const index = this.selectedLabel.indexOf(target_label.id)
      if (index === -1) {
        this.selectedLabel.push(target_label.id)
        emitInfo.action = 'add'
      } else {
        this.selectedLabel.splice(index, 1)
        emitInfo.action = 'remove'
      }

      emitInfo.labels = this.selectedLabel
      this.$emit('onLabelChange', emitInfo)
    },
    clearSelectedLabels () {
      for (const labelName of this.selectedLabel) {
        this.$emit('onLabelChange', {
          name: labelName,
          action: 'remove',
          labels: []
        })
      }
      this.selectedLabel = []
      this.searchStr = ''
    },
    changeLabelModalOpenState () {
      this.$refs.labelModal.toggal()
    }
  }
}
</script>
