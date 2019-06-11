<template>
  <Card shadow @mouseover.native="isDisplayDate=false" @mouseout.native="isDisplayDate=true" @click.native="jump(notice)" style="cursor:pointer">
    <p slot="title" style="line-height:16px">
      <Row>
        <Col span="16">
          <div :title="notice.sender.file">
            <span style="display:inline-block;max-width:270px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
              {{notice.sender.file}}
            </span>
            <Badge v-if="notice.count > 1" :count="notice.count" class-name="notice-badge" style="padding-left:5px"></Badge>
          </div>
        </Col>
        <Col span="8" align="right">
          <div v-if="isDisplayDate">
            <p style="font-weight:400;font-size:12px">
              {{timestampToTime(notice.timestamp)}}
            </p>
          </div>
          <div v-else>
            <a><Icon type="md-close" @click.stop="deleteNotice(notice.key)"/></a>
          </div>
        </Col>
      </Row>
    </p>
    <p style="word-break:break-all">{{notice.title}}</p>
    <Row>
      <Col span="20">
        <p>
          <b><a href="#"> </a></b>
        </p>
      </Col>
      <Col span="24" align="right">
        <a href="#" @click.stop="changeNoticeStatusToFalse(notice)" title="Don't remind again">
          <Icon type="ios-eye-off" style="font-size:16px"/>
        </a>
      </Col>
    </Row>
  </Card>
</template>

<script>
export default {
  name: "noticeMessage",
  props: ["notice"],
  data() {
    return {
      isDisplayDate: true,
      jumpToUrl: null,
      jumpToName: null
    };
  },
  methods: {
    timestampToTime(timeStamp){
      let dateObj = new Date(timeStamp * 1000)
      let month = dateObj.getMonth()+1
      let date = dateObj.getDate()
      let hour = dateObj.getHours()
      let minute = (dateObj.getMinutes() < 10 ? '0'+dateObj.getMinutes() : dateObj.getMinutes())
      let second = (dateObj.getSeconds() < 10 ? '0'+dateObj.getSeconds() : dateObj.getSeconds())
      return month + '/' + date + ' ' + hour + ':' + minute + ':' + second
    },
    deleteNotice(noticeKey){
      this.$store.dispatch('deleteNotice', noticeKey)
    },
    jump(notice) {
      this.$bus.$emit('toggleNotice')
      // TODO: support select manifest
      // store.state.manifest[0]: only one manifest are supported in v1.0
      for(const menuItem of this.$store.state.menu){
        if (menuItem['params'] && this.$store.state.manifest[0] === menuItem['params']['name']){
          this.$store.commit('setActiveName', menuItem.title)
          this.jumpToUrl = menuItem.params.src + '?' + 'event_id=' + this.notice.id
          this.jumpToName = menuItem.params.name
          break
        }
      }
      this.$store.commit('plugin/setSrc', this.jumpToUrl)
      this.$router.push({name:'plugin-view', params:{name:this.jumpToName, query:'event_id='+this.notice.id}})
      // this.$store.dispatch("createIssue", notice)
      this.$store.dispatch('deleteNotice', notice.key)
    },
    changeNoticeStatusToFalse(notice) {
      this.$store.dispatch('updateNoticeStatus', {
        key:notice.key,
        status:false
      })
    }
  }
}
</script>

<style>
.ivu-card > .ivu-card-head{
  padding: 5px 5px 3px 5px;
  font-size: 12px;
}
.ivu-card > .ivu-card-body{
  padding: 5px 5px 5px 8px;
  font-size: 12px;
}
</style>
