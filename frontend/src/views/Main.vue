<template>
<div>
    <Layout class="main-layout">
        <Sider ref="mainSider" class="sider-bar" hide-trigger collapsible :collapsed-width="50" v-model="isCollapsed">
            <div class="logo">
                <span>{{logo}}</span>
            </div>
            <Divider class="sider-bar-divider"/>
            <Menu theme="dark" width="auto" :class="menuitemClasses" :active-name="activeName">
              <MenuItem v-for="(menuItem, index) in menu" :key="index" :name="menuItem.title" @click.native="menuItemOnClick(menuItem)">
                <b>{{menuItemTitle(menuItem)}}</b>
              </MenuItem>
            </Menu>
        </Sider>
        <Layout>
            <Header class="main-header" inline>
                <Icon type="md-menu" color="white" size="24" @click.native="collapsedSider"></Icon>
            </Header>
            <Content>
                <div class="main-container">
                  <router-view></router-view>
                </div>
            </Content>
            <Footer class="main-footer">
              <span class="main-footer-copyright">
                <strong style="color:#f8f8f9">Copyright &copy; 2018-present <a href="http://www.meituan.com">Meituan</a>. All rights reserved.</strong>
              </span>
              <Poptip v-if="status" content="content" placement="top-end" class="main-footer-status" width="200">
                <a>
                  <Icon type="ios-arrow-up" style="color:#f8f8f9"/>
                  <b style="color:#f8f8f9">&nbsp;&nbsp;Version {{status.version}}</b>
                </a>
                <div slot="title"><b>💡Status</b></div>
                <div slot="content">
                  <Row v-for="value in showedStatus" :key="value" :gutter="16">
                    <i-col span=12><b style="float: right">{{value}}</b></i-col>
                    <i-col span=12>{{status[value]}}</i-col>
                  </Row>
                </div>
              </Poptip>
            </Footer>
        </Layout>
    </Layout>
</div>
</template>

<script>
import io from 'socket.io-client'
import Notice from '@/views/Notice.vue'

export default {
  name: 'MainLayout',
  components: {
    Notice
  },
  data() {
    return {
      isCollapsed: true,
      alertIO: null,
      showedStatus: ["ip", "mock.port", "proxy.port", "version"]
    }
  },
  created(){
    this.$Notice.config({
      top: 0,
    });
    this.alertIO = io('/alert')
    this.alertIO.on('show', this.showNotice);
  },
  destroyed() {
    this.alertIO.close()
  },
  mounted(){
    this.$store.dispatch('loadMenu')
    this.$store.dispatch('loadStatus')
    this.$store.dispatch('loadManifest')
  },
  computed: {
    menuitemClasses(){
      return ["menu-item", this.isCollapsed ? "collapsed-menu" : "menu"];
    },
    logo(){
      if(this.isCollapsed){
        return 'L'
      }else{
        return 'Lyrebird'
      }
    },
    menu(){
      return this.$store.state.menu
    },
    status(){
      return this.$store.state.status
    },
    manifest(){
      return this.$store.state.manifest
    },
    activeName(){
      return this.$store.state.activeName
    }
  },
  methods: {
    showNotice(data){
      this.$Notice.warning({
        duration: 0,
        title: null,
        render() {
          return (<Notice data={data}></Notice>)
        }
      });
    },
    collapsedSider() {
      this.$refs.mainSider.toggleCollapse();
    },
    menuItemTitle(menuItem){
      if(this.isCollapsed){
        return menuItem.title.substring(0,1)
      }else{
        return menuItem.title
      }
    },
    menuItemOnClick(menuItem){
      this.$store.commit('setActiveName', menuItem.title)
      if(menuItem.type==='router'){
        if(menuItem.name === 'plugin-view'){
          this.$store.commit('plugin/setSrc', menuItem.params.src);
        }
        this.$router.push({name:menuItem.name, params:menuItem.params});
      }else{
        window.open(menuItem.path, '_self');
      }
    }
  }
};
</script>

<style scoped>
.main-layout {
  height: 100vh;
}
.sider-bar {
  background-color: #515a6e;
}
.sider-bar-divider {
    height: 1px;
    margin: 0;
    background: #6c6c6c;
}
.logo {
  height: 38px;
  text-align: center;
}
.logo span{
    color: white;
    font-size: 28px;
    font-weight: bolder;
    font-style: italic;
}
.main-header {
  height: 38px;
  line-height: 38px;
  padding: 0;
  margin: 0;
  background-color: #0fccbf;
}
.main-footer {
  height: 28px;
  line-height: 28px;
  padding: 0;
  background-color: #0fccbf;
}
.main-footer-copyright {
  font-size: 12px;
  margin-left: 15px;
  color: #f8f8f9;
}
.main-footer-status {
  float: right;
  font-size: 11px;
  margin-right: 10px
}
.collapsed-menu span {
  width: 0px;
  transition: width 0.2s ease;
}
.menu-item span {
  display: inline-block;
  overflow: hidden;
  width: 69px;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
  transition: width 0.2s ease 0.2s;
}
.main-container {
  padding: 5px;
  height: calc(100vh - 66px);
}
</style>

