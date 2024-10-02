<script setup>
import { ref, defineExpose } from 'vue'
const error = ref('')
const show = (err) => {
    error.value = "<p>" + (err.message ? err.message : err) + "</p>" +
        (err.response? "<p>" + err.response.data.error.join("<br/>") + "</p>" : "")
    console.error((err.message ? err.message : err) + " ==> " + (err.response ? err.response.data.error : ""));
}
const reset = () => {
    error.value = '';
}
defineExpose({ show, reset })
</script>

<template>
    <li class="api-error" v-if="error !== ''" v-html="error"></li>
</template>

<style scoped>
.api-error {
    margin: 1em auto;
    margin-bottom: 4em;
    padding: 0.5em 1em 0.5em 1em;
    border: 0px;
    border-radius: 1.5em;
    box-shadow: 0em 0em 0.5em 0.5em rgba(255, 255, 255, 0.3);
    background-color: #f44;
    color: #ddd
}
</style>