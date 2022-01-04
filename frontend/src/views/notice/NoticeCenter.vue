<template>
  <div class="main-header-notice" @click="drawerIsCollapsed=true">
    <v-badge
      color="error"
      :content="noticeList.length > 999 ? '999+' : noticeList.length"
      :value="noticeList.length"
      offset-x="10"
      offset-y="16"
      class="main-header-notice-badge"
    >
      <v-icon>
        mdi-bell-outline
      </v-icon>
    </v-badge>

    <v-navigation-drawer
      v-model="drawerIsCollapsed"
      app
      absolute
      temporary
      hide-overlay
      right
      class="side-navgation-right"
      width="400"
      color="rgba(230, 230, 230, 0.6)"
    >
      <div class="drawer-header">
        <ButtonGroup>
          <Button v-for="tab in tabList" :key="tab" :class="[setResultClass(tab)]" @click="setTargetTab(tab)"><p>{{tab}}</p></Button>
        </ButtonGroup>
      </div>
      <div v-if="selectedTab === tabList[0]">
        <div v-if="noticeList.length" style="height:calc(100% - 31px);overflow-x:auto">
          <div v-for="(notice, index) in noticeList" :key="index" style="padding: 5px 10px;">
            <NoticeMessage :notice="notice" :alert="true"/>
          </div>
        </div>
        <div v-else class="notice-empty">
          <p>No New Notifications</p>
        </div>
      </div>
      <div v-else-if="selectedTab === tabList[1]">
        <div v-if="notRemindList.length" style="height:calc(100% - 31px);overflow-x:auto">
          <div v-for="(notice, index) in notRemindList" :key="index" style="padding: 5px 10px;">
            <NoticeMessage :notice="notice" :alert="false"/>
          </div>
        </div>
        <div v-else class="notice-empty">
          <p>Nothing here</p>
        </div>
      </div>
    </v-navigation-drawer>
  </div>
</template>

<script>
import Alert from '@/views/notice/Alert.vue'
import NoticeMessage from '@/views/notice/NoticeMessage.vue'

export default {
  name: "noticeCenter",
  components: {
    Alert,
    NoticeMessage
  },
  data() {
    return {
      offset: [15, 4],
      selectedTab : "Notifications",
      tabList : ["Notifications", "NotRemind"],
      count: 0,
      drawerIsCollapsed: false
    };
  },
  created(){
    this.$bus.$on('toggleNotice', this.toggle)
    this.$io.on('alert', this.showNoticeAlert)
    this.$io.on('update', this.updateNotice)
    this.$store.dispatch('loadNoticeCenterData')
  },
  destroyed() {
    this.$io.removeListener('alert', this.showNoticeAlert)
    this.$io.removeListener('update', this.updateNotice)
  },
  computed: {
    noticeList() {
      return this.$store.state.notice.noticeList
    },
    notRemindList() {
      return this.$store.state.notice.notRemindList
    }
  },
  methods: {
    showNoticeAlert(noticeInfo){
      this.$Notice.warning({
        duration: 3,
        title: null,
        render() {
          return (<Alert noticeInfo={noticeInfo}></Alert>)
        }
      });
    },
    updateNotice(){
      this.$store.dispatch('loadNoticeCenterData')
    },
    setTargetTab(selectedTab){
      this.selectedTab = selectedTab
    },
    setResultClass(tab){
      if(tab === this.selectedTab){
        return 'ivu-btn-selected'
      }
      else{
        return 'ivu-btn-unselected'
      }
    },
    toggle(){
      this.drawerIsCollapsed = !this.drawerIsCollapsed
    }
  }
};
</script>

<style>
.main-header-notice {
  float: right;
  margin-right: 15px;
}
.main-header-notice-badge {
  cursor: pointer;
}
.drawer-header {
  height: 38px;
  padding: 12px;
  text-align: center;
}
.notice-badge{
  box-shadow:0 0 0 transparent !important;
  border: 0px !important;
  padding:0 3px !important;
  line-height: 14px !important;
  height: 14px !important;
}
.notice-badge-gray{
  background: #bbbbbb !important;
  box-shadow:0 0 0 transparent !important;
  border: 0px !important;
  padding:0 3px !important;
  line-height: 14px !important;
  height: 14px !important;
}
.notice-empty{
  position: absolute;
  top:40%;
  left:50%;
  transform:translate(-50%,-50%);
  text-align: center;
}
.ivu-btn-group > .ivu-btn-selected {
  border: none;
  height: 20px;
  font-size: 12px;
  font-weight: 700;
  line-height: 20px;
  padding: 0 36px;
}
.ivu-btn-group > .ivu-btn-unselected {
  border: none;
  height: 20px;
  font-size: 12px;
  line-height: 20px;
  padding: 0 36px;
  background: #cccccc;
  color: #ffffff;
}
.side-navgation-right p {
  margin-bottom: 0px;
}
</style>
