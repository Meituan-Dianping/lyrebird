<template>
<div>
    <Layout class="main-layout">
        <Sider ref="mainSider" class="sider-bar" hide-trigger collapsible :collapsed-width="50" v-model="isCollapsed">
            <div class="logo">
                <span>{{logo}}</span>
            </div>
            <Divider class="sider-bar-divider"/>
            <Menu theme="dark" width="auto" :class="menuitemClasses" active-name="Inspector">
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

            </Footer>
        </Layout>
    </Layout>
</div>
</template>

<script>
import io from 'socket.io-client'
const alertIO = io('/alert')
export default {
  name: 'MainLayout',
  data() {
    return {
      isCollapsed: true
    };
  },
  created: function(){
    this.$Notice.config({
      top: 0,
    });
    alertIO.on('show', data => {
      this.$Notice.warning({
        duration: 0,
        title: null,
        render: h => {
          return h('div', [
            h('div', data.message),
            h('a', {
                attrs: {
                    href: '#',
                },
                on: {
                    click: () => {
                        this.jump(data)
                    }
                }
            }, 'Create new issue')
          ])
          }
        });
      });
  },
  mounted(){
    this.$store.dispatch('loadMenu')
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
    }
  },
  methods: {
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
      if(menuItem.type==='router'){
        if(menuItem.name === 'plugin-view'){
          this.$store.commit('setSrc', menuItem.params.src);
        }
        this.$router.push({name:menuItem.name, params:menuItem.params});
      }else{
        window.open(menuItem.path, '_self');
      }
    },
    jump(data) {
      let url = '/ui/plugin/lyrebird-bugit?source=overbridgeAlert&alertContext='+encodeURIComponent(data.message)+'&msg='+encodeURIComponent(JSON.stringify(data))
      this.$store.commit('setSrc', url);
      this.$router.push({name:'plugin-view'});
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
    font-size: 30px;
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
  padding: 0;
  background-color: #0fccbf;
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

