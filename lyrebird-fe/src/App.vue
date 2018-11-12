<template>
  <div id="app">
      <Layout>
        <Sider :style="{overflow:'auto',height: 'calc(100vh - 28px)'}" ref="side1" hide-trigger collapsible :collapsed-width="78" v-model="isCollapsed">
          <Menu active-name="home" theme="dark" width="auto"> 
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
          <Header :style="{background: '#fff'}">
            <Icon @click.native="collapsedSider"  type="md-menu" ></Icon>
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
      isCollapsed: true,
      comps: [
        {
          name: "home",
          path: "/",
          icon: "ios-navigate"
        },
        {
          name: "about",
          path: "/about",
          icon: "ios-search"
        },
        {
          name: "hello",
          path: "/hello",
          icon: "ios-search"
        }
      ]
    };
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
  overflow-y: hidden
}
</style>

<style scoped>
.layout-footer-bar {
  position: fixed;
  bottom: 0px;
  width:100%;
  height:28px;
  background:black;
}
</style>


