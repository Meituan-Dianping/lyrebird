<template>
  <Modal v-model="shown" title="Mock data selector">
    <div v-if="activatedGroups">
      <label style="padding-right:5px">Activated Mock Group:</label>
      <Tag v-for="group in activatedGroups" :key="group.id">{{group.name}}</Tag>
    </div>
    <Input search enter-button v-model="searchStr" @on-search="searchGroup"></Input>
    <div class="searchlist">
      <div v-for="item in searchResults" :key="item.id" class="searchitem">
        <Row type="flex" justify="center" align="middle">
          <Col span="20">
            <label class="searchitem-title">{{item.name}}</label>
            <p class="searchitem-path">{{item.abs_parent_path}}</p>
          </Col>
          <Col span="4">
            <Button style="float: right" @click="onActivateClick(item.id)">
              <Icon type="ios-play" color="green" />
            </Button>
          </Col>
        </Row>
      </div>
    </div>
    <div slot="footer"></div>
  </Modal>
</template>

<script>
import { searchGroupByName, getActivatedGroup } from '@/api'

export default {
  data () {
    return {
      searchStr: '',
      shown: false,
      searchResults: []
    }
  },
  created () {
    this.searchGroup()
  },
  computed: {
    activatedGroups () {
      return this.$store.state.inspector.activatedGroup
    }
  },
  methods: {
    toggal () {
      this.shown = !this.shown
    },
    searchGroup () {
      searchGroupByName(this.searchStr)
        .then(response => {
          this.searchResults = response.data.data
        }).catch(error => { })
    },
    onActivateClick (groupId) {
      this.$store.dispatch('activateGroup', groupId)
    }
  },
}
</script>

<style>
.searchlist {
  margin-top: 5px;
  padding: 5px 0 5px;
  max-height: 60vh;
  overflow-y: auto;
}
.searchitem {
  border: 1px solid gainsboro;
  border-radius: 3px;
  padding: 1px 5px 1px;
  margin: 1px 0px 1px;
}
.searchitem-title {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.searchitem-path {
  color: gray;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
