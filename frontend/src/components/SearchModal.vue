<template>
  <Modal v-model="shown" title="Mock data selector" width="60%" :styles="{top: '80px'}" :footer-hide=true>
    <slot name="selected"></slot>
    <Input search enter-button v-model="searchStr" @on-search="searchGroup"></Input>
    <div class="searchlist">
      <div v-for="item in searchResults" :key="item.id">
      <slot name="searchItem" :searchResult="item"></slot>
      </div>
    </div>
  </Modal>
</template>

<script>
import { searchGroupByName } from '@/api'

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
  methods: {
    toggal () {
      this.shown = !this.shown
    },
    searchGroup () {
      searchGroupByName(this.searchStr)
        .then(response => {
          this.searchResults = response.data.data
        }).catch(error => { })
    }
  }
}
</script>

<style>
.searchlist {
  margin-top: 5px;
  padding: 5px 0 5px;
  max-height: 60vh;
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
