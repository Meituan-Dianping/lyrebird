<template>
  <div class="flow-list">
    <v-data-table
      class="flow-table"
      checkbox-color="primary"
      :height="tableSize.height"
      show-select
      fixed-header
      calculate-widths
      hide-default-footer
      v-model="selectedFlows"
      v-resize="onTableResize"
      :header-props="{sortIcon:'mdi-menu-down'}"
      :headers="headers"
      :items="flowList"
      :page.sync="currentPage"
      :items-per-page="pageSize"
      @click:row="selectFlow"
      :item-class="getFlowTableItemClass"
    >

      <template v-slot:item.source="{ item }">

        <span class="flow-list-item-source">
          <v-chip label small
            v-if="item.status === 'kill'"
            class="flow-list-item-tag"
            color="#fff1f0"
            text-color="#f5222d"
          >kill</v-chip>
          <v-chip label small
            v-else-if="item.response.mock === 'mock'"
            class="flow-list-item-tag"
            color="primaryBrightest"
            text-color="primary"
          >mock</v-chip>
          <v-chip label small
            v-else-if="item.response.mock === 'proxy'"
            color="border"
            class="flow-list-item-tag"
            text-color="accent"
          >proxy</v-chip>
          <v-chip label small
            v-else
            class="flow-list-item-tag"
            color="border"
            text-color="content"
          >pending</v-chip>
        </span>

        <v-tooltip bottom v-if="item.proxy_response">
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on" class="flow-list-item-source">
              <v-chip label small
                class="flow-list-item-tag"
                color="#FFF7E2"
                text-color="#D69600"
              >diff</v-chip>
            </span>
          </template>
          <span>Get the server response while the request is mocked</span>
        </v-tooltip>

        <v-tooltip bottom v-if="item.status === 'ssr'">
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on" class="flow-list-item-source">
              <v-chip label small
                class="flow-list-item-tag"
                color="#FFF7E2"
                text-color="#D69600"
              >SSR</v-chip>
            </span>
          </template>
          <span>Put mock data in request body instead of response data</span>
        </v-tooltip>

        <v-tooltip bottom v-if="getRequestEditors(item).length">
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on" class="flow-list-item-source">
              <v-icon x-small color="accent">mdi-wrench</v-icon>
            </span>
          </template>
          <p>Request modification:</p>
          <p v-for="(value, index) in getRequestEditors(item)" :key=index style="line-height:1">{{index + 1}}. {{value.name}}</p>
        </v-tooltip>
      </template>

      <template v-slot:item.method="{ item }">
        <span>{{ item.request.method }}</span>
      </template>

      <template v-slot:item.status="{ item }">
        <span>
          <span v-if="item.response.code >= 400" class="flow-list-status-error">{{ item.response.code }}</span>
          <span v-else>{{ item.response.code }}</span>
        </span>
      </template>

      <template v-slot:item.request="{ item }">
        <v-row class="my-0 ml-0 mr-1">
          <span class="flow-list-item-url" :style="{maxWidth:urlMaxWidth+'px'}">
            <span>{{ item.request.scheme }}</span>
            <span v-if="item.request.scheme">://</span>

            <span class="flow-list-item-url-host">{{ item.request.host}}</span>
            <span v-show="item.request.port" class="flow-list-item-url-host">:{{ item.request.port}}</span>
            <span class="flow-list-item-url-path">{{ item.request.path}}</span>

            <span class="flow-list-item-url-params" v-if="item.request.params">?</span>
            <span class="flow-list-item-url-params">{{ item.request.params }}</span>
          </span>

          <v-spacer/>

          <span class="flow-list-item-copy-btn" @click.stop>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">
                  <v-btn 
                  icon
                  x-small
                  plain
                  @click="generateCurlUrl(item)"
                  >
                    <v-icon
                      x-small
                      color="accent"
                    >mdi-xml</v-icon>
                  </v-btn>
                </span>
              </template>
              Copy as cURL
            </v-tooltip>
          </span>

          <span class="flow-list-item-copy-btn" @click.stop>
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">
                  <v-btn 
                    icon
                    x-small
                    plain
                    @mousedown.prevent="showPopup($event, item)"
                    @mouseup="handleButtonMouseUp"
                  >
                    <v-icon
                      x-small
                      color="accent"
                      v-clipboard:copy="item.request.url"
                      v-clipboard:success="onUrlCopy"
                      v-clipboard:error="onUrlCopyError"
                    >mdi-content-copy</v-icon>
                  </v-btn>
                </span>
              </template>
              Copy Url
            </v-tooltip>
          </span>
          <div v-if="isCopyPopupVisible" class="copyPopup" :style="copyPopupStyle">
            <v-btn small text @mouseup="copyPartialUrl('Host')">Host</v-btn>
            <v-btn small text @mouseup="copyPartialUrl('Path')">Path</v-btn>
            <v-btn small text @mouseup="copyPartialUrl('Query')">Query</v-btn>
          </div>
        </v-row>
      </template>

      <template v-slot:item.start_time="{ item }">
        <span>{{timestampToTime(item.start_time)}}</span>
      </template>

      <template v-slot:item.duration="{ item }">
        <span>{{readablizeDuration(item.duration)}}</span>
      </template>

      <template v-slot:item.size="{ item }">
        <span>{{readablizeBytes(item.size)}}</span>
      </template>

    </v-data-table>

    <v-row class="inspector-tabel-pagination-row">
      <v-spacer />
      <v-col class="pa-0 pt-2">
        <v-pagination
          v-model="currentPage"
          :length="pageCount"
          @input="refreshFlowList"
          total-visible=7
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { readablizeBytes, timestampToTime } from '@/utils'
import { debounce } from 'lodash';

export default {
  name: 'flowList',
  components: {
  },
  data () {
    return {
      urlMaxWidth:0,
      resizeObserver:null,
      tableSize: {
        width: 0,
        height: 0,
      },
      flowList: [],
      displayFlowList: [],
      focusedFlowIdx: null,
      debouncedKeyboardSelectFlow: null,
      refreshFlowListTimer: null,
      refreshTimer: null,
      refreshGapTime: 1,
      refreshMaxGapTime: 3600,
      lastRefreshTime: 0,
      displayFlowCount: 0,
      pageSize: 50,
      pageCount: 0,
      currentPage: 1,
      isCopyPopupVisible: false,
      copyPopupStyle: {
        top: '0px',
        left: '0px'
      },
      currentItem: null,
      isMouseOverButton: false,
      headers: [
        {
          text: 'Source',
          value: 'source',
          sortable: false,
          width: 105
        },
        {
          text: 'Method',
          value: 'method',
          sortable: false,
          filterable: false,
          width: 60
        },
        {
          text: 'Status',
          value: 'status',
          sortable: false,
          filterable: false,
          width: 50
        },
        {
          text: 'URL',
          value: 'request',
          sortable: false,
        },
        {
          text: 'Start',
          value: 'start_time',
          filterable: false,
          width: 70
        },
        {
          text: 'Duration',
          value: 'duration',
          filterable: false,
          width: 70
        },
        {
          text: 'Size',
          value: 'size',
          filterable: false,
          width: 70
        }
      ]
    }
  },
  created () {
    this.$io.on('action', this.resetRefreshGapTime)
    this.refreshTimer = setInterval(() => {
        if(this.lastRefreshTime == this.refreshGapTime){
          this.reload()
          this.lastRefreshTime = 1;
          this.refreshGapTime = this.refreshGapTime << 1
          if(this.refreshGapTime > this.refreshMaxGapTime){
            this.refreshGapTime = this.refreshMaxGapTime
          }
        }
        this.lastRefreshTime += 1
      }, 1000)
  },
  mounted () {
    this.initResizeObserver();
    // The maximum number of clicks per second is limited to 4 times. 
    // Too high click frequency may cause jumping if the refresh is not timely
    this.debouncedKeyboardSelectFlow = debounce(this.keyboardSelctFlow, 250);
    document.addEventListener('keydown', this.debouncedKeyboardSelectFlow);
    document.addEventListener('mouseup', this.handleGlobalMouseUp);
  },
  beforeDestroy () {
    document.removeEventListener('keydown', this.debouncedKeyboardSelectFlow);
    document.removeEventListener('mouseup', this.handleGlobalMouseUp);
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
  },
  destroyed () {
    this.$io.removeListener('action', this.resetRefreshGapTime)
    clearInterval(this.refreshTimer)
  },
  computed: {
    originFlowList () {
      return this.$store.state.inspector.originFlowList
    },
    searchStr () {
      return this.$store.state.inspector.searchStr
    },
    focusedFlowDetail () {
      return this.$store.state.inspector.focusedFlowDetail
    },
    selectedFlows: {
      get () {
        return this.$store.state.inspector.selectedFlows
      },
      set (val) {
        this.$store.commit('setSelectedFlows', val)
        this.itemSelectChange(val)
      }
    }
  },
  watch: {
    originFlowList () {
      this.refreshFlowList()
    },
    searchStr (newValue, oldValue) {
      clearTimeout(this.refreshFlowListTimer)
      this.refreshFlowListTimer = setTimeout(() => {
        if (newValue !== oldValue) {
          this.focusedFlowDetail = null
          this.refreshFlowList()
          clearTimeout(this.refreshFlowListTimer)
        }
      }, 500)
    },
    focusedFlowDetail (newValue, oldValue) {
      if(!newValue)
        this.focusedFlowIdx = null
    }
  },
  methods: {
    reload () {
      this.$store.dispatch('loadFlowList')
    },
    resetRefreshGapTime () {
      this.refreshGapTime = 1
      this.lastRefreshTime = 1
    },
    initResizeObserver() {
      const tableWrapper = this.$el.querySelector('.v-data-table__wrapper');
      if (tableWrapper) {
        const debouncedCalculateUrlMaxWidth = debounce((width) => {
          this.calculateUrlMaxWidth(width);
        }, 250);
        this.resizeObserver = new ResizeObserver(entries => {
          for (let entry of entries) {
            debouncedCalculateUrlMaxWidth(entry.contentRect.width);
          }
        });
        this.resizeObserver.observe(tableWrapper);
      }
    },
    calculateUrlMaxWidth(tableWidth){
      /* widths of fixed columns
      source: 105px
      method: 60px
      status: 50px
      start_time: 70px
      duration: 70px
      size: 70px
      */
      const otherColumnsWidth=105+60+50+70+70+70;
      this.urlMaxWidth=tableWidth-otherColumnsWidth
    },
    onTableResize () {
      const height = window.innerHeight - 44 - 40 - 12 - 26 - 7 - 1 - 8 - 32 - 12 - 12 - 28
      /* reset table height
      Header 44px
      Title 40px
      padding 12px
      buttonbar 26px
      buttombar margin-bottom 7
      divider 1
      tabel
      margin-top 8px
      pagination 32px
      padding 12px
      margin-bottom 12px
      Footer 28px
      */
      this.tableSize = { 
        width: 800,
        height: height
      }
    },
    getFlowTableItemClass(item) {
      if (!this.focusedFlowDetail) {
        return ''
      }
      if (item.id === this.focusedFlowDetail.id) {
        return 'flow-list-item-focused'
      }
    },
    selectFlow (flow, item) {
      this.$store.dispatch('focusFlow', flow)
      // flowList is a stack structure where new data is added to the header, 
      // so a negative index is used here to ensure consistency when the data changes
      this.focusedFlowIdx = item.index + (this.currentPage-1)*this.pageSize - this.displayFlowList.length
    },
    keyboardSelctFlow (event) {
      if(!this.focusedFlowDetail)
        return
      if(this.focusedFlowIdx == null)
        return
      if(event.key == "ArrowUp") {
        this.keyboardUpSelctFlow()
      }else if(event.key == "ArrowDown") {
        this.keyboardDownSelectFlow()
      }
    },
    keyboardUpSelctFlow () {
      let currentIdx = this.displayFlowList.length + this.focusedFlowIdx
      if(currentIdx <= 0)
        return
      if(currentIdx <= (this.currentPage-1)*this.pageSize){
        this.currentPage -= 1
        this.refreshFlowList()
      }
      this.focusedFlowIdx -= 1
      this.$store.dispatch('focusFlow', this.displayFlowList[currentIdx-1]) 
    },
    keyboardDownSelectFlow () {
      let currentIdx = this.displayFlowList.length + this.focusedFlowIdx
      if(currentIdx >= this.displayFlowList.length-1)
        return
      if(currentIdx >= this.currentPage*this.pageSize-1){
        this.currentPage += 1
        this.refreshFlowList()
      }
      this.focusedFlowIdx += 1
      this.$store.dispatch('focusFlow', this.displayFlowList[currentIdx+1])
    },
    itemSelectChange (event) {
      let selectedIds = []
      for (const row of event) {
        selectedIds.push(row.id)
      }
      this.$store.commit('setSelectedId', selectedIds)
    },
    filterMethod (value, option) {
      return option.toUpperCase().indexOf(value.toUpperCase()) !== -1
    },
    isMatchByAnd (url, searchList) {
      for (const searchItem of searchList)
        if (!searchItem || !this.filterMethod(searchItem, url)) 
          return false
      return true
    },
    isMatch (url, searchList) {
      for (const searchItem of searchList) 
        if(this.isMatchByAnd(url, searchItem))
          return true
      return false
    },
    refreshFlowList () {
      this.displayFlowList = []
      let searchStr = typeof(this.searchStr) === 'string' ? this.searchStr.trim() : ''

      // Search
      if(!searchStr){
        this.displayFlowList = this.originFlowList
      } else {
        // Split searchStr by one or more (spaces, |)
        let searchStrList = searchStr.split(/\|+/)
        for(const idx in searchStrList){
          searchStrList[idx] = searchStrList[idx].trim()
          searchStrList[idx] = searchStrList[idx].split(/\s+/)
        }
        for (const flow of this.originFlowList) {
          this.isMatch(flow.request.url, searchStrList) ? this.displayFlowList.push(flow) : null
        }
      }

      // Page
      this.displayFlowCount = this.displayFlowList.length
      this.pageCount = Math.max(Math.ceil(this.displayFlowCount / this.pageSize), 1)
      this.currentPage = this.pageCount && (this.currentPage > this.pageCount) ? this.pageCount : this.currentPage
      const startIndex = (this.currentPage - 1) * this.pageSize
      const endIndex = startIndex + this.pageSize
      this.flowList = this.displayFlowList.slice(startIndex, endIndex)

      // Select
      let displayFlowSelectedIdSet = new Set()
      for (const flow of this.flowList) {
        if (this.$store.state.inspector.selectedIds.includes(flow.id)) {
          flow['_checked'] = true
          displayFlowSelectedIdSet.add(flow.id)
        }
      }
      for (const i in this.selectedFlows) {
        if (!displayFlowSelectedIdSet.has(this.selectedFlows[i].id)) {
          this.$store.commit('removeSelectedFlowsByIndex', i)
        }
      }
    },
    getRequestEditors (row) {
      let displayRowAction = []
      for (const action of row.action) {
        if (action.id === 'mock') {
          continue
        }
        displayRowAction.push(action)
      }
      return displayRowAction
    },
    readablizeBytes (size) {
      return readablizeBytes(size)
    },
    timestampToTime (timestamp) {
      return timestampToTime(timestamp)
    },
    readablizeDuration (duration) {
      if (duration >= 1) {
        return Math.round(duration * 100 / 100) + 's'
      } else {
        return (duration * 1000).toFixed(0) + 'ms'
      }
    },
    getSourceTooltipContent (row) {
      if (row.status === 'kill') {
        return 'Request is killed by lyrebird'
      } 
      return row.response.mock
    },
    generateCurlUrl(item){
      this.$store.dispatch('getFlowDetailForCmd', item.id)
    },
    onUrlCopy () {
      this.$bus.$emit('msg.success', 'URL copied!')
    },
    onUrlCopyError (e) {
      this.$bus.$emit('msg.error', 'Copy url error:' + e)
    },
    showPopup(event, item) {
      event.preventDefault();
      this.currentItem = item;
      this.isMouseOverButton = true;

      // Clear any existing timer
      if (this.popupTimer) {
        clearTimeout(this.popupTimer);
      }

      // Set a new timer
      this.popupTimer = setTimeout(() => {
        this.isCopyPopupVisible = true;
        this.$nextTick(() => {
          const button = event.target.closest('button');
          const popup = this.$el.querySelector('.copyPopup');
          if (button && popup) {
            const buttonRect = button.getBoundingClientRect();
            const popupRect = popup.getBoundingClientRect();
            this.copyPopupStyle = {
              bottom: `${window.innerHeight - buttonRect.top}px`,
              left: `${buttonRect.left + (buttonRect.width / 2) - (popupRect.width / 2)}px`
            };
          }
        });
      }, 200);
    },
    handleButtonMouseUp() {
      if (this.popupTimer) {
        clearTimeout(this.popupTimer);
      }
      if (this.isMouseOverButton && !this.isCopyPopupVisible) {
        this.copyUrl();
      }
      this.hidePopup();
    },
    handleGlobalMouseUp() {
      if (this.popupTimer) {
        clearTimeout(this.popupTimer);
      }
      this.hidePopup();
    },
    hidePopup() {
      this.isCopyPopupVisible = false;
      this.currentItem = null;
      this.isMouseOverButton = false;
    },
    copyPartialUrl(name) {
      let urlinfo = ''
      if (name == 'Host') {
        urlinfo = this.currentItem.request.host
      } else if (name == 'Path') {
        urlinfo = this.currentItem.request.path
      } else if (name == 'Query') {
        urlinfo = this.currentItem.request.params
      }
      if (urlinfo && urlinfo.trim() !== '') {
        this.$bus.$emit('clipboard', urlinfo)
      } else {
        this.$bus.$emit('msg.error', `Skip copy, ${name} is empty`)
      }
    }
  }
}
</script>

<style lang="css">
.flow-table table > thead > tr > th{
  padding: 0px !important;
  height: 30px !important;
  font-size: 12px !important;
  background-color: #FAF9FA !important;
}
.flow-table table > thead > tr > th > span{
  color: #000520 !important;
}
.flow-table table > thead > tr > th > div > div > i{
  padding-left: 5px;
  font-size: 18px !important;
}
.flow-table table > tbody > tr > td {
  padding: 0px !important;
  height: 36px !important;
  font-size: 12px !important;
}
.flow-table table > tbody > tr > td > div > div > i {
  padding-left: 5px;
  font-size: 18px !important;
}
.flow-table table>tbody>tr>td>span {
  color: #666 !important;
}
.flow-table table>tbody>tr>td>div {
  color: #666 !important;
}
.flow-table {
  width: 100%;
}
.flow-list-item-source > span {
  padding: 0px 8px !important;
}
.flow-list-item-focused {
  background-color: #5b57c41A;
}
.inspector-tabel-pagination-row {
  margin: 0 !important;
  padding: 0 !important;
}
.inspector-tabel-pagination-row .v-pagination {
  justify-content: right;
}
.inspector-tabel-pagination-row .v-pagination__navigation {
  margin: 5px !important;
  height: 30px;
  width: 30px;
  box-shadow: none !important;
  background-color: #F9F8FA !important;
}
.inspector-tabel-pagination-row .v-pagination .v-pagination__item {
  margin: 5px !important;
  height: 30px;
  min-width: 30px;
  box-shadow: none !important;
}
.inspector-tabel-pagination-row .v-pagination .v-pagination__item:not(.v-pagination__item--active) {
  margin: 5px !important;
  height: 30px;
  min-width: 30px;
  box-shadow: none !important;
  background-color: #F9F8FA !important;
}
</style>

<style scoped>
.flow-list {
  width: 100%;
  overflow-y: auto;
}
.flow-list .v-data-table>.v-data-table__wrapper>table {
  width: calc(100% - 20px) !important;
}
.flow-list-item-source {
  text-transform: capitalize;
  padding: 0px;
}
.flow-list-item-tag {
  margin: 0px 2px;
}
.flow-list-status-error {
  color: #F51818;
  font-weight: 400;
}
.flow-list-item-url {
  display: inline-block;
  word-break: keep-all;
  width: calc(100% - 100px);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}
.flow-list-item-url-scheme {
  color: unset;
}
.flow-list-item-url-host {
  color: #5F5CCA;
  font-weight: 400;
}
.flow-list-item-url-path {
  color:#318CD7;
  font-weight: 400;
}
.flow-list-item-url-params {
  color: unset;
}
.flow-list-item-copy-btn {
  display: inline-block;
  overflow: hidden;
  cursor: pointer;
}
.copyPopup {
  position: fixed;
  background-color: white;
  border: 1px solid #e0e0e0;
  padding: 2px;
  z-index: 1000;
  display: flex;
  flex-direction: row;
  border-radius: 4px;
}


</style>
