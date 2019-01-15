<template>
  <div class="main-header-notice" @click="drawerIsCollapsed=true">
    <a>
      <Badge :count="noticeList.length" :offset="offset" class-name="notice-badge">
        <Icon type="ios-notifications" size="16" color="white" ></Icon>
      </Badge>
    </a>
    <Drawer title="Notice" width="380" :closable="true" :mask="false" v-model="drawerIsCollapsed" >
      <div v-for="notice in noticeList" style="padding: 5px 10px;">
        <NoticeMessage :notice="notice"></NoticeMessage>
      </div>
    </Drawer>
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
      offset: [15, 2],
      count: 0,
      noticeList: [],
      drawerIsCollapsed: false
    };
  },
  created(){
    this.$Notice.config({
      top: 0,
    });
    this.$io.on('show', this.showNotice);
  },
  methods: {
    showNotice(noticeInfo){
      console.log('from drawer', noticeInfo);
      this.$store.commit('addNotice', noticeInfo)
      this.noticeList = this.$store.state.notice.noticeList
      console.log('from drawer', this.noticeList);
      this.$Notice.warning({
        duration: 3,
        title: null,
        render() {
          return (<Alert noticeInfo={noticeInfo}></Alert>)
        }
      });
    }
  }
};
</script>

<style>
.main-header-notice {
 float: right;
 margin-right: 15px;
}
.notice-badge{
  background: #FF7F55 !important;
  box-shadow:0 0 0 transparent !important;
  border: 0px !important;
  padding:0 3px !important;
  line-height: 14px !important;
  height: 14px !important;
}
.ivu-drawer-right > .ivu-drawer-content {
  background:  rgba(230,230,230,0.8);
}
.ivu-drawer-content > .ivu-drawer-header {
  height: 38px;
}
.ivu-drawer-content > .ivu-drawer-body {
  padding: 0px;
}
</style> 