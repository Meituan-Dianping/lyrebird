<template>
    <div style="height:100%">
        <iframe :src="src" frameborder="0" class="plugin-frame" @load="onLoad"></iframe>
    </div>
</template>

<script>   
    export default {
        computed:{
            src() {
                let src = this.$store.state.plugin.src
                return src
            }
        },
        methods: {
            onLoad(event){
                console.log('plugins view on load', this.src)
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
