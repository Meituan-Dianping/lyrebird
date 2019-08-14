<template>
    <div>
        <label v-if="jsonPath">
            <strong>Json Path:</strong>
            <span class="json-path-str">{{jsonPath}}</span>
        </label>
    </div>
</template>

<script>
export default {
    computed: {
        jsonPath() {
            return this.$store.state.dataManager.jsonPath
        }
    }
};
</script>

<style scoped>
.json-path-str{
    font-style: italic
}
</style>
