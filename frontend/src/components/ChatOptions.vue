<script setup>
import { onMounted, ref, defineProps, defineEmits, defineExpose } from 'vue';
import { apiClient } from './ApiClient.js';
const emit = defineEmits(['errorReset', 'setAnswer', 'messagesReset', 'scrollDownChat', 'handleError', 'stream']);
// Props
const props = defineProps({
    user: String,
    loading: Boolean,
    enableDelete: Boolean
});
// Reactive data
const hideSettings = ref(true);
const history = ref("My history");
const models = ref([]);
const model = ref("");
const ability = ref("Eres un asistente especializado en ingenieria de software.");
const question = ref('Dame un ejemplo de código TensorFlow en python, así como la instalación con conda de las librerias necesarias.');
const showHelp = ref(false)
// Methods
const stream = () => {
    if (props.loading) return;
    emit('stream', question.value);
}
const deleteChat = () => {
    if (!props.enableDelete) return;
    emit('errorReset');
    apiClient.get(`/api/v1/chat/delete/${props.user}`)
        .then(() => emit('messagesReset'))
        .catch(e => emit('handleError', e));
}
const getModels = () => {
    emit('errorReset');
    apiClient.get('/api/v1/models')
        .then(res => models.value = res.data.response)
        .catch(e => emit('handleError', e));
}
const toggleSettings = () => {
    hideSettings.value = !hideSettings.value;
    emit('scrollDownChat');
}
const toggleHelp = () => showHelp.value = !showHelp.value;

defineExpose({ model, ability, history, question, showHelp });
onMounted(() => getModels())
</script>

<template>
    <div class="chat-container" style="margin-top: 1em;">
        <div>
            <div>
                <div style="float: left; margin-right: 1em; width: 100%">
                    <div style="float: right">
                        <img style="width: 4em; height: 4em;" src="../assets/chatgpt/send.webp" @click="stream"
                            :style="loading ? 'filter: brightness(50%)' : ''" alt="Ask AI (ctrl+enter)"
                            title="Ask AI (ctrl+enter)">
                    </div>
                    <textarea rows="4" cols="50" v-model="question" class="text_input" placeholder="Message..."
                        autofocus v-on:keypress.ctrl.enter="stream"></textarea>
                    <!-- <img class="optionIcon" src="../assets/chatgpt/plus.webp" alt="Add another text" title="Add another text">
                    <img class="optionIcon" src="../assets/chatgpt/collapse.webp" alt="Add another text" title="Add another text"> -->
                </div>
            </div>
            <div style="clear:both">
                <img class="optionIcon" src="../assets/chatgpt/settings.webp" alt="Settings" title="Settings"
                    @click="toggleSettings">
                <img class="optionIcon" src="../assets/chatgpt/trash.webp" alt="Delete chat" title="Delete chat"
                    @click="deleteChat" :style="enableDelete ? '': 'filter: brightness(50%)'">
                <img class="optionIcon" src="../assets/chatgpt/help.webp" alt="Show help" title="Show help"
                    @click="toggleHelp" :style="enableDelete ? '': 'filter: brightness(50%)'">
            </div>
        </div>
        <div :hidden="hideSettings" style="clear: both; margin-top: 4em">
            <input type="text" class="text_input" v-model="ability"
                placeholder="Artificial intelligence system ability (describe any ability in natural language)"
                title="Artificial intelligence system ability (describe any ability in natural language)" />
        </div>
        <div :hidden="hideSettings">
            <input type="text" class="text_input" v-model="history" placeholder="Current chat history"
                title="Current chat history" />
        </div>
        <div :hidden="hideSettings">
            <select v-model="model" id="model" name="model" placeholder="Select model" title="Select model"
                v-if="models" class="text_input">
                <option value="">Select llm model...</option>
                <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
            </select>
        </div>
    </div>
</template>

<style scoped>
.chat-container {
    background-color: rgba(0, 0, 0, 0.4);
    border-radius: 1.5em;
    box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
    padding: 1em;
    position: relative;
    margin-left: 2em;
    margin-right: 2em;
}

.text_input {
    background-color: black;
    color: white;
    font-size: 16px;
    /* position: absolute; */
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1em 0em 1em 1em;
    margin-bottom: 1em;
    width: 92%;
}

textarea {
    /* resize: vertical; */
    -webkit-box-sizing: border-box;
    -moz-box-sizing: border-box;
    box-sizing: border-box;
}

button:disabled {
    cursor: not-allowed;
}

button:disabled img {
    filter: brightness(50%)
}

.optionIcon {
    border-radius: 50%;
    box-shadow: 0px 0px 10px 5px rgba(26, 21, 21, 0.7);
    object-fit: cover;
    position: relative;
    float: right;
    width: 3em;
    height: 3em;
    margin-left: 0.3em;
}
</style>