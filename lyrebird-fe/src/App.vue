<template>
  <div id="app">
      <Layout>
        <Sider :style="{overflow:'auto',background: '#fff', height: 'calc(100vh - 28px)'}" 
          ref="side1" hide-trigger collapsible :collapsed-width="78" v-model="isCollapsed">
          <Menu active-name="home" theme="light" width="auto" :class="menuitemClasses"> 
            <MenuItem 
                    v-for="comp in comps" 
                    :key="comp.name" 
                    :name="comp.name" 
                    :to="comp.path">
                        <Icon :type="comp.icon"></Icon>
                        <span>{{comp.name}}</span>
            </MenuItem>                    
          </Menu>
        </Sider>
        <Layout>
          <Header :style="{background: '#6699CC', padding: '0 0 0 0',height:'50px'}">
            <Icon @click.native="collapsedSider"  :class="rotateIcon" :style="{color: '#fff',margin: '0 0 10px 20px'}" type="md-menu" size="24" ></Icon>
          </Header>
          <Content :style="{overflow:'auto',height: 'calc(100vh - 28px)',}">
            <router-view/>
          </Content>  
        </Layout>
      </Layout>   
      <div class="layout-footer-bar">
        Footer
      </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isCollapsed: false,
      comps: this.$store.state.comps
    };
  },
  computed: {
    rotateIcon() {
      return ["menu-icon", this.isCollapsed ? "rotate-icon" : ""];
    },
    menuitemClasses() {
      return ["menu-item", this.isCollapsed ? "collapsed-menu" : ""];
    }
  },
  methods: {
    collapsedSider() {
      this.$refs.side1.toggleCollapse();
    }
  }
};
</script>
<style>
body {
  overflow-x: hidden;
  overflow-y: hidden;
}
</style>

<style scoped>
.layout-footer-bar {
  position: fixed;
  bottom: 0px;
  width: 100%;
  height: 28px;
  background: #666666;
}

.menu-icon {
  transition: all 0.3s;
}
.rotate-icon {
  transform: rotate(-90deg);
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
.menu-item i {
  transform: translateX(0px);
  transition: font-size 0.2s ease, transform 0.2s ease;
  vertical-align: middle;
  font-size: 16px;
}
.collapsed-menu span {
  width: 0px;
  transition: width 0.2s ease;
}
.collapsed-menu i {
  transform: translateX(5px);
  transition: font-size 0.2s ease 0.2s, transform 0.2s ease 0.2s;
  vertical-align: middle;
  font-size: 22px;
}
</style>


