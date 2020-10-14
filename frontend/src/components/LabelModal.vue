<template>
  <div>
    <Modal v-model="shown" width="70%" :styles="{top: '80px'}" :footer-hide=true >

      <p class="modal-title">
        <b>{{labelList.length}} labels</b>
        <Button
          type="success"
          size="small"
          style="float:right;"
          @click="isAddingNewLabel=!isAddingNewLabel, getRandomColor()"
        >
        New label
        </Button>
      </p>

      <Table
        v-if="isAddingNewLabel"
        :columns="newLabelColumns"
        :data="[{}]"
        disabled-hover
        :show-header="false"
        :row-class-name="getRowClassName"
      >

        <template slot="name">
          <p class="new-label-title">
            <span style="color:red;font-size:12px;padding-right:3px;">*</span>
            <b>Label name</b>
          </p>
          <Input
            type="text"
            size="small"
            v-model="newLabelName"
            placeholder="Label name"
            class="new-label-input"
          />
        </template>

        <template slot="color">
          <p class="new-label-title">
            <b>Color</b>
          </p>
          <Button size="small" icon="md-refresh" shape="circle"
            :style="'margin-bottom:12px;color:white;background-color:' + newLabelColor" 
            @click="getRandomColor"
          />
          <Input
            type="text"
            size="small"
            v-model="newLabelColor"
            placeholder="RGB #ff6600"
            class="new-label-input"
            style="width:80px;"
          />
        </template>

        <template slot="description">
          <p class="new-label-title">
            <b>Description</b>
          </p>
          <Input
            type="text"
            size="small"
            v-model="newLabelDescription"
            placeholder="Label description"
            class="new-label-input"
          />
        </template>

        <template slot="preview">
          <p class="new-label-title">
            <b>Preview</b>
          </p>
          <p class="new-label-input">
            <p
              class="modal-label"
              :style="'background-color:'+(newLabelColor?newLabelColor:'#808695')">
              {{newLabelName?newLabelName:'Label'}}
            </p>
          </p>
        </template>

        <template slot-scope="{ row, index }" slot="action">
          <p style="padding:12px 0px;">&nbsp</p>
          <p style="margin-bottom:12px;">
            <a @click="handleCreate" style="margin-right:10px">Create</a>
            <a @click="isAddingNewLabel=false" style="color:#808695">Cancel</a>
          </p>
        </template>
      </Table>

      <Table
        :columns="labelColumns"
        :data="labelList"
        disabled-hover
        :max-height="isAddingNewLabel?(500-80):500"
        style="margin-top:16px;width:100%"
      >

        <template slot-scope="{ row, index }" slot="name">
          <Input v-if="index === editIndex"  type="text" size="small" v-model="editName" />
          <span
            v-else
            class="modal-label"
            :style="'background-color:'+(row.color?row.color:'#808695')"
          >
            {{row.name}}
          </span>
        </template>

        <template slot-scope="{ row, index }" slot="color">
          <Input v-if="index === editIndex"  type="text" size="small" v-model="editColor" />
          <span
            v-else
            class="modal-label"
            :style="'background-color:'+(row.color?row.color:'#808695')"
          >
            {{row.color}}
          </span>
        </template>

        <template slot-scope="{ row, index }" slot="description">
          <Input v-if="index === editIndex"  type="text" size="small" v-model="editDescription" />
          <span v-else>{{row.description}}</span>
        </template>

        <template slot-scope="{ row, index }" slot="info">
          <Tooltip 
            content="No group related, this label will disappear when Lyrebird restart."
            max-width="350"
            placement="bottom-end"
          >
            <Icon
              v-show="row.groups.length===0"
              size="12"
              type="md-information-circle"
              color="#f60"
              style="padding-right:5px"
            />
          </Tooltip>
          <span>
            {{(row.groups.length===0?'No':row.groups.length) + (row.groups.length>1 ? ' related groups' : ' related group')}}
          </span>
        </template>

        <template slot-scope="{ row, index }" slot="action">
          <div v-if="index === editIndex" >
            <a @click="handleSave(row, index)" style="margin-right:10px">Save</a>
            <a @click="editIndex = -1">Cancel</a>
          </div>
          <div v-else-if="editIndex>-1">
            <Button type="text" size="small" disabled>Edit</Button>
            <Button type="text" size="small" disabled>Delete</Button>
          </div>
          <div v-else-if="editIndex === -1">
            <a @click="handleEdit(row, index)" style="margin-right:10px">Edit</a>
            <a @click="handleDelete(row, index)" style="color:#808695">Delete</a>
          </div>
        </template>
      </Table>
    </Modal>
    <Modal v-model="showDeleteModal">
      <p slot="header" style="color:#f60;text-align:center">
        <Icon type="ios-information-circle"></Icon>
        <span>Delete confirmation</span>
      </p>
      <div style="text-align:center;font-size:14px">
        <p>
          Are you sure you want to delete label <b>{{deleteIndex>-1?labelList[deleteIndex].name:''}}</b>?
        </p>
        <p><b>{{deleteIndex>-1?labelList[deleteIndex].groups.length:''}} related groups</b> will delete this label!</p>
      </div>
      <div slot="footer">
        <Button size="small" type="primary" @click="showDeleteModal=false">Cancel</Button>
        <Button type="text" size="small" @click="removeLabel" style="color:#ed4014" :loading="isDeleting">
          Delete
        </Button>
      </div>
    </Modal>
    <Modal v-model="showSaveModal">
      <p slot="header" style="color:#f60;text-align:center">
        <Icon type="ios-information-circle"></Icon>
        <span>Save confirmation</span>
      </p>
      <div style="text-align:center;font-size:14px">
        <p>
          Are you sure you want to change label <b>{{editIndex>-1?labelList[editIndex].name:''}}</b>?
        </p>
        <p><b>{{editIndex>-1?labelList[editIndex].groups.length:''}} related groups</b> will be changed!</p>
      </div>
      <div slot="footer">
        <Button size="small" type="primary" @click="showSaveModal=false">Cancel</Button>
        <Button type="text" size="small" @click="changeLabel" style="color:#2d8cf0" :loading="isSaving">
          Save
        </Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import { createLabels, updateLabel, deleteLabel } from '@/api'

export default {
  data () {
    return {
      shown: false,
      searchStr: '',
      editIndex: -1,
      deleteIndex: -1,
      editName: '',
      editColor: '',
      editDescription: '', 
      newLabelName: '',
      newLabelColor: '',
      newLabelDescription: '', 
      defaultLabelColor: [
        '#2b85e4',
        '#808695',
        '#17233d',
        '#ed4014',
        '#ff9900',
        '#19be6b',
        '#2db7f5',
        '#19bebf',
        '#f3c045'
      ],
      isSaving: false,
      isDeleting: false,
      showSaveModal: false,
      showDeleteModal: false,
      isAddingNewLabel: false,
      labelColumnsName: {
        title: 'Name',
        slot: 'name',
        width: 200
      },
      labelColumnsDescription: {
        title: 'Description',
        slot: 'description'
      },
      labelColumnsInfo: {
        title: 'Info',
        slot: 'info',
        width: 150
      },
      labelColumnsAction: {
        title: 'Action',
        slot: 'action',
        width: 150,
        align: 'center'
      },
      labelColumnsColor: {
        title: 'Color',
        slot: 'color',
        width: 150
      },
      labelColumnsPreview: {
        title: 'Preview',
        slot: 'preview',
        width: 150
      }
    }
  },
  computed: {
    labelColumns () {
      return [
        this.labelColumnsName,
        this.labelColumnsColor,
        this.labelColumnsDescription,
        this.labelColumnsInfo,
        this.labelColumnsAction
      ]
    },
    newLabelColumns () {
      return [
        this.labelColumnsName,
        this.labelColumnsColor,
        this.labelColumnsDescription,
        this.labelColumnsPreview,
        this.labelColumnsAction
      ]
    },
    labelList() {
      let labelList = []
      const labels = this.$store.state.dataManager.labels
      for (const key in labels) {
        labelList.push(labels[key])
      }
      return labelList
    }
  },
  methods: {
    toggal () {
      this.shown = !this.shown
      this.isAddingNewLabel = false
    },
    handleCreate () {
      const label = {
        name: this.newLabelName,
        color: this.newLabelColor,
        description: this.newLabelDescription
      }
      createLabels(label)
        .then(_ => {
          this.$store.dispatch('loadDataLabel')
          this.isAddingNewLabel = false
          this.newLabelName = ''
          this.newLabelColor = ''
          this.newLabelDescription = ''
          this.$bus.$emit('msg.success', 'Label ' + label.name + ' created!')
        })
        .catch(error => {
          this.$bus.$emit('msg.error', 'Create label ' + label.name + ' error: ' + error.data.message)
        })
    },
    getRowClassName (row, index) {
      return 'new-label-row'
    },
    getRandomColor () {
      const randomInt = parseInt(Math.random() * this.defaultLabelColor.length)
      this.newLabelColor = this.defaultLabelColor[randomInt]
    },
    handleEdit (row, index) {
      this.editIndex = index
      this.editName = row.name
      this.editColor = row.color
      this.editDescription = row.description
    },
    handleSave (row, index) {
      if (row.groups.length > 0) {
        this.showSaveModal = true
      } else {
        this.changeLabel()
      }
    },
    changeLabel () {
      const label = this.labelList[this.editIndex]
      label.name = this.editName
      label.color = this.editColor
      label.description = this.editDescription
      this.isSaving = true
      updateLabel(label)
        .then(_ => {
          this.$store.commit('setDataListSelectedLabel', [])
          this.$store.dispatch('loadDataLabel')
          this.isSaving = false
          this.showSaveModal = false
          this.shown = false
          this.editIndex = -1
          this.editName = ''
          this.editColor = ''
          this.editDescription = ''
          this.$store.dispatch('loadDataMap')
          if (this.$store.state.dataManager.groupDetail.id) {
            this.$store.dispatch('loadGroupDetail', this.$store.state.dataManager.groupDetail)
          }
          this.$bus.$emit('msg.success', 'Label ' + label.name + ' saved! ' + label.groups.length + ' related groups updated!')
         })
        .catch(error => {
          this.isSaving = false
          this.$bus.$emit('msg.error', 'Save label ' + label.name + ' error: ' + error.data.message)
       })
    },
    handleDelete (row, index) {
      this.deleteIndex = index
      if (row.groups.length > 0) {
        this.showDeleteModal = true
      } else {
        this.removeLabel()
      }
    },
    removeLabel () {
      const label = this.labelList[this.deleteIndex]
      this.isDeleting = true
      deleteLabel(label.id)
        .then(_ => {
          this.$store.dispatch('loadDataLabel')
          this.deleteIndex = -1
          this.showDeleteModal = false
          this.isDeleting = false
          this.$store.dispatch('loadDataMap')
          if (this.$store.state.dataManager.groupDetail.id) {
            this.$store.dispatch('loadGroupDetail', this.$store.state.dataManager.groupDetail)
          }
          this.$bus.$emit('msg.success', 'Label ' + label.name + ' delete. ' + label.groups.length + ' related groups updated!')
         })
        .catch(error => {
          this.deleteIndex = -1
          this.isDeleting = false
          this.$bus.$emit('msg.error', 'Delete label ' + label.name + ' error: ' + error.data.message)
       })
    }
  }
}
</script>

<style>
.modal-title {
  font-size: 14px;
  padding: 25px 0px 10px 2px;
}
.new-label-title {
  margin:12px 0px;
}
.new-label-input {
  margin-bottom: 12px;
}
.modal-label {
  font-size: 12px;
  padding: 2px 6px;
  margin-left: 5px;
  color:white;
  border-radius: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  max-width: 100%;
}
.ivu-table .new-label-row td{
  background-color: #f8f8f9;
}
</style>
