<template>
    <div style="height:100%">
        <iframe :src="src" frameborder="0" class="plugin-frame"></iframe>
    </div>
</template>

<script>   
    export default {
        computed:{
            src(){
                console.log(this.$route.params.src);
                return this.$route.params.src
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
