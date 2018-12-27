<template>
    <div style="height:100%">
        <iframe :src="src" frameborder="0" class="plugin-frame"></iframe>
    </div>
</template>

<script>   
    export default {
        props:['name'],
        computed:{
            src() {
                let src = this.$store.state.plugin.src
                return src
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
