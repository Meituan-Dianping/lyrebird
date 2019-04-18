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
                if(this.$route.params.query){
                    src = src + '?' + this.$route.params.query
                }
                return src
            }
        },
        methods: {
            onLoad(event){
                console.log('plugins view on load', this.src, this.$route)
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
