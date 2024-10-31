<script lang="ts" setup>
import { AxiosError } from 'axios';
import { ref, defineExpose } from 'vue'
const error = ref('')
const message = ref('')
const showError = (err: AxiosError | String) => {
    if (err instanceof AxiosError) {
        error.value = "<p>" + err.message + "</p>" +
            (err.response ? "<p>" + err.response.data.error.join("<br/>") + "</p>" : "")
        console.error((err.message) + " ==> " + (err.response ? err.response.data.error : ""));
        return;
    }
    error.value = "<p>" + err + "</p>"
    console.error(err);
}
const showMessage = (msg) => {
    message.value = msg;
}
const reset = () => {
    error.value = '';
    message.value = ''
}
defineExpose({ showError, showMessage, reset })
</script>

<template>
    <li class="message" v-if="message !== ''" v-html="message"></li>
    <li class="error" v-if="error !== ''" v-html="error"></li>
</template>

<style scoped>
li {
    margin: 1em auto;
    padding: 0.5em 1em 0.5em 1em;
    border: 0px;
    border-radius: 1.5em;
    box-shadow: 0em 0em 0.5em 0.5em rgba(255, 255, 255, 0.3);
}

.error {
    background-color: #f44;
    color: #ddd
}

.message {
    background-color: #070;
    color: #ddd
}
</style>