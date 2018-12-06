<template>
    <div style="height:100%">
        <iframe :src="src" frameborder="0" class="plugin-frame"></iframe>
    </div>
</template>

<script>   
    export default {
        computed:{
            src() {
                let name = this.$route.params.name
                let menu = this.$store.state.menu
                // 取出store中的menu进行匹配，返回插件src地址
                if(menu){
                    for (let i=0; i< menu.length; i++){
                        if(typeof(menu[i].params)=="object" && menu[i].params.name == name){
                            // 优先判断是否是本身带参（如notice点击跳转），其次触发menu的逻辑
                            return this.$route.params.src || this.$store.state.menu[i].params.src
                        }
                    }
                }
            }
        }
    }
</script>

<style>
.plugin-frame {
    position: relative;
    height: 100%;
    width: 100%; 
}
</style>
