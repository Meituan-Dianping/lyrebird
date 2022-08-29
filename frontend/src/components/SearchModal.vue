<template>
  <Modal v-model="shown" :title="title?title:defaultTitle"  width="60%" :styles="{top: '80px'}" :footer-hide=true>
    <slot name="modalHeader"></slot>
    <slot name="selected"></slot>
    <Input search enter-button size="small" v-model="searchStr" @on-search="searchGroup" placeholder="Search name/id"></Input>
    <div class="searchlist">
      <div v-for="item in searchResults" :key="item.id">
      <slot name="searchItem" :searchResult="item"></slot>
      </div>
    </div>
    <slot name="modalFooter"></slot>
  </Modal>
</template>

<script>
import { searchGroupByName } from '@/api'

export default {
  props: ['showRoot', 'title'],
  data () {
    return {
      searchStr: '',
      shown: false,
      searchResults: [],
      defaultTitle: "Mock Data Selector"
    }
  },
  created () {
    this.searchGroup()
  },
  methods: {
    toggal () {
      this.shown = !this.shown
    },
    searchGroup () {
      searchGroupByName(this.searchStr)
        .then(response => {
          this.searchResults = response.data.data
          for (const searchItem in this.searchResults) {
            if (!this.searchResults[searchItem].parent_id) {
              this.$store.commit('setImportSnapshotParentNode',this.searchResults[searchItem])
              break
            }
          }
          if (!this.showRoot) {
            for (const index in this.searchResults) {
              if (!this.searchResults[index].parent_id) {
                this.searchResults.splice(index, 1)
                break
              }
            }
          }
        }).catch(error => { })
    }
  }
}
</script>

<style>
.searchlist {
  margin-top: 5px;
  padding: 5px 0 5px;
  max-height: 40vh;
  overflow-y: auto;
}
.search-row {
  border-bottom: 1px dashed gainsboro;
  cursor: pointer;
}
.search-row:hover {
  background-color: #f8f8f9;
}
.search-item {
  padding: 5px 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  max-width: 100%;
}
.search-item-title {
  font-size: 14px;
  padding: 0px 5px;
}
.search-item-path {
  font-size: 12px;
  color: #808695;
  padding: 0px 5px;
}
.search-item-btn {
  padding: 0px 5px;
  cursor: pointer;
}
</style>
