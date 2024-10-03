<template>
    <div class="chat-container" style="margin-top: 1em;">
        <div class="buttons" :hidden="hideSettings">
            <input type="text" class="text_input" v-model="ability"
                placeholder="Artificial intelligence system ability (describe any hability in natural language)"
                title="Artificial intelligence system ability (describe any hability in natural language)" />
        </div>
        <div class="buttons" :hidden="hideSettings">
            <input type="text" class="text_input" v-model="history" placeholder="Current chat history"
                title="Current chat history" />
        </div>
        <div class="buttons" :hidden="hideSettings">
            <select v-model="model" id="model" name="model" placeholder="Select model" title="Select model" v-if="models">
                <option value="">Select llm model...</option>
                <option v-for="m in models" :key="m" :value="m">{{m}}</option>
            </select>
        </div>
        <div>
            <img class="optionIcon" src="../assets/veloai/settings.png" alt="Delete chat" title="Settings"
                @click="toggleSettings">
        </div>
        <div :hidden="hideSettings">
            <img class="optionIcon" src="../assets/veloai/trash.png" alt="Delete chat" title="Delete chat"
                @click="deleteChat">
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref, defineProps, defineEmits, defineExpose } from 'vue';
import ApiClient from './ApiClient.js';
const emit = defineEmits(['errorReset', 'setAnswer', 'messagesReset', 'scrollDownChat', 'handleError']);
// Props
const props = defineProps({
    user: String
});
// Reactive data
const hideSettings = ref(true);
const history = ref("My history");
const models = ref([]);
const model = ref("");
const ability = ref("Eres un asistente especializado en ingenieria de software.");
// Methods
const deleteChat = () => {
    emit('errorReset');
    // TODO: remove setAnswer emit -> emit('setAnswer', 'Waiting for response...');
    ApiClient.get(`/api/v1/chat/delete/${props.user}`).then(() => {
        emit('messagesReset');
    }).catch(e => emit('handleError', e));
}
const getModels = () => {
    emit('errorReset');
    ApiClient.get('/api/v1/models').then(res => {
        models.value = res.data.response
    }).catch(e => emit('handleError', [e]));
}
const toggleSettings = () => {
    hideSettings.value = !hideSettings.value;
    emit('scrollDownChat');
}
defineExpose({ model, ability, history });
onMounted(() => {
    getModels();
})
</script>

<style scoped>
.buttons {
    background-color: rgba(0, 0, 0, 0.4);
    border-radius: 1.5em;
    box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
    padding: 1em;
    position: relative;
    clear: both;
    min-width: 5em;
    margin-top: 1em;
    margin-left: 1em;
    margin-right: 1em;
}
</style>