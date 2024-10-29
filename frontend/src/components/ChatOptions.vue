<script setup>
import { onMounted, ref, defineProps, defineEmits, defineExpose } from 'vue';
import { apiClient } from './ApiClient.js';
import { insertAtCursor } from './utils.js';
import FileUploader from './FileUploader.vue'

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
const question = ref('Genera un ejemplo de código completo con TensorFlow en python.');
const showHelp = ref(false)
const fileUploader = ref('');
const message = ref();
const showFileAssist = ref(false);

let fileAssistText = ''  // TODO: REFACTOR MOVE fileAssist TO COMPONENT
let fileSelectedIndex = 0
const fileAssistLeft = ref(0)
const fileAssistTop = ref(0)
// TODO: GET FILES FROM SERVER
const filesAvailable = ['App.vue', 'ApiClient.js', 'ChatContainer.vue', 'ChatError.vue', 'ChatHeader.vue', 'ChatHelp.vue', 'ChatMessage.vue', 'ChatOptions.vue', 'FileUploader.vue', 'iconSets.ts', 'utils.js', 'main.js']
const filesAvailableFiltered = ref([])
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
const uploadFiles = (formData) => {
    emit('errorReset');
    let total = 0;
    apiClient.postForm('/api/v1/upload-files', formData, {
        onUploadProgress: function (e) {
            fileUploader.value.showProgress(e.loaded, e.total);
            total = e.total;
        }
    }).then(() => {
        fileUploader.value.showProgress(total, total);
    }).catch(e => {
        fileUploader.value.setShowUploadButton(true);
        emit('handleError', e);
        return false;
    });
}
const openDialog = (input) => {
    fileUploader.value.openDialog(input);
}
const shortCuts = (e) => { // TODO: REFACTOR MOVE fileAssist TO COMPONENT
    var key = e.key;
    // console.log("key=" + key + " e.ctrlKey=" + e.ctrlKey);
    if (key == '@') {
        filesAvailableFiltered.value = filesAvailable;
        fileAssistTop.value = e.clientY;
        fileAssistLeft.value = e.clientX;
        showFileAssist.value = true;
        fileSelectedIndex = 0;
        fileAssistText = '@';
    } else if (showFileAssist.value) {
        if (key == 'Backspace') {
            fileAssistText = fileAssistText.substring(0, fileAssistText.length - 1);
            if (fileAssistText.length == 0) showFileAssist.value = false;
            else filterFilesAvailable();
        } else if (key == 'Escape') showFileAssist.value = false;
        else if (e.ctrlKey && key == 'Enter') stream();
        else if (key == 'Enter') {
            selectFile(fileSelectedIndex);
            e.preventDefault();
        } else if (key == 'ArrowUp' || key == 'ArrowLeft') fileSelectedMove(-1);

        else if (key == 'ArrowDown' || key == 'ArrowRight') fileSelectedMove(1);
        else if (showFileAssist.value && key != 'Shift' && key != 'Control' && key != 'AltGraph' && key != 'Alt') {
            fileAssistText += key;
            filterFilesAvailable();
        }
    }
}
const fileSelectedMove = (move) => { // TODO: REFACTOR MOVE fileAssist TO COMPONENT
    if (move == 1) {
        if (fileSelectedIndex < filesAvailableFiltered.value.length - 1)
            fileSelectedIndex++;
    } else {
        if (fileSelectedIndex > 0)
            fileSelectedIndex--;
    }
    // console.log("fileSelectedIndex=" + fileSelectedIndex);
    filesAvailableFilteredUpdateView(filesAvailableFiltered.value);
}
const filterFilesAvailable = () => { // TODO: REFACTOR MOVE fileAssist TO COMPONENT
    const text = fileAssistText.toLowerCase().substring(1);
    const regex = new RegExp('(' + text + ')', 'ig');
    const filtered = filesAvailable
        .filter(f => f.toLowerCase().indexOf(text) != -1)
        .map(f => f.replace(regex, '<span style="color: yellow">$1</span>'));
    if (fileSelectedIndex >= filtered.length) fileSelectedIndex = filtered.length
    filesAvailableFilteredUpdateView(filtered);
}
const filesAvailableFilteredUpdateView = (filtered) => {// TODO: REFACTOR MOVE fileAssist TO COMPONENT
    filesAvailableFiltered.value = [];
    filesAvailableFiltered.value = filtered;
}
const selectFile = (idx) => { // TODO: REFACTOR MOVE fileAssist TO COMPONENT
    const offset = -fileAssistText.length
    // console.log("selectFile fileAssistText=" + fileAssistText + ", offset=" + offset);
    const fileName = filesAvailableFiltered.value[idx].replace('<span style="color: yellow">', '').replace('</span>', '');
    question.value = insertAtCursor(document.getElementById("textarea-question"), ' @' + fileName + ' ', offset);
    showFileAssist.value = false;
}


defineExpose({ model, ability, history, question, showHelp });
onMounted(() => getModels())
</script>

<template>
    <div class="options-container" style="margin-top: 1em;">
        <div>
            <div>
                <div class="container">
                    <ul>
                        <li style="width: 100%">
                            <textarea rows="4" cols="50" v-model="question" class="base-input textarea"
                                placeholder="Message..." autofocus @keydown="shortCuts" ref="message"
                                id="textarea-question"></textarea>
                        </li>
                        <li>
                            <img src="../assets/chatgpt/send.webp" @click="stream"
                                :class="'sendIcon' + (loading ? ' disabled' : '')" alt="Ask AI (ctrl+enter)"
                                title="Ask AI (ctrl+enter)">
                        </li>
                    </ul>
                    <!-- TODO: REFACTOR MOVE fileAssist TO COMPONENT -->
                    <div v-if="showFileAssist" class="fileAssist"
                        :style="'left: ' + fileAssistLeft + 'px; top: ' + fileAssistTop + 'px;'">
                        <ul>
                            <li v-for="(file, idx) in filesAvailableFiltered" :key="idx" @click="selectFile(idx)"
                                v-html="file" :class="fileSelectedIndex == idx ? 'selected' : ''"></li>
                        </ul>
                    </div>
                    <FileUploader @uploadFiles="form => uploadFiles(form)" ref="fileUploader" v-slot="fileUploaderSlot">
                        <img class="optionIconSmall" src="../assets/chatgpt/close.webp"
                            @click="fileUploaderSlot.removeFile(index)" alt="Attach folder" title="Attach folder">
                    </FileUploader>
                    <!--<img class="optionIcon" src="../assets/chatgpt/plus.webp" alt="Add another text" title="Add another text">-->
                </div>
            </div>
            <div style="clear:both">
                <img class="optionIcon" src="../assets/chatgpt/folder.webp" @click="openDialog('folder-picker')"
                    alt="Attach folder" title="Attach folder">
                <img class="optionIcon" src="../assets/chatgpt/file.webp" @click="openDialog('file-picker')"
                    alt="Attach file(s)" title="Attach file(s)">
                <img class="optionIcon" src="../assets/chatgpt/settings.webp" alt="Settings" title="Settings"
                    @click="toggleSettings">
                <img class="optionIcon" src="../assets/chatgpt/trash.webp" alt="Delete chat" title="Delete chat"
                    @click="deleteChat" :class="enableDelete ? '' : 'disabled'">
                <img class="optionIcon" src="../assets/chatgpt/help.webp" alt="Show help" title="Show help"
                    @click="toggleHelp" :class="enableDelete ? '' : 'disabled'">
            </div>
        </div>
        <div :hidden="hideSettings" style="clear: both; margin-top: 4em">
            <input type="text" class="base-input input" v-model="ability"
                placeholder="Artificial intelligence system ability (describe any ability in natural language)"
                title="Artificial intelligence system ability (describe any ability in natural language)" />
        </div>
        <div :hidden="hideSettings">
            <input type="text" class="base-input input" v-model="history" placeholder="Current chat history"
                title="Current chat history" />
        </div>
        <div :hidden="hideSettings">
            <select v-model="model" id="model" name="model" placeholder="Select model" title="Select model"
                v-if="models" class="base-input input">
                <option value="">Select llm model...</option>
                <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
            </select>
        </div>
    </div>
</template>

<style scoped>
.options-container {
    background-color: rgba(0, 0, 0, 0.4);
    border-radius: 1.5em;
    box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
    padding: 1em;
    position: relative;
    margin-left: 2em;
    margin-right: 2em;
}

.container {
    float: left;
    margin-right: 1em;
    width: 100%;
    display: block;
}

.base-input {
    background-color: black;
    color: white;
    font-size: 16px;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 0.2em 0em 0.2em 0.2em;
    margin-bottom: 0.3em;
}

.input {
    width: 92%;
}

.textarea {
    width: 99%;
}

textarea {
    margin-bottom: 0px;
    -webkit-box-sizing: border-box;
    -moz-box-sizing: border-box;
    box-sizing: border-box;
}

button:disabled {
    cursor: not-allowed;
}

img.disabled {
    filter: brightness(50%);
    cursor: not-allowed;
}

.optionIcon {
    border-radius: 50%;
    box-shadow: 0px 0px 10px 5px rgba(26, 21, 21, 0.7);
    object-fit: cover;
    width: 2.5em;
    height: 2.5em;
    margin-left: 0.3em;
    cursor: pointer;
}

.sendIcon {
    width: 4em;
    height: 4em;
    cursor: pointer;
}

.optionIconSmall {
    width: 1.2em;
    height: 1.2em;
    position: relative;
    top: 0.2em;
}

.right {
    position: relative;
    float: right;
}

.left {
    position: relative;
    float: left;
}

.container ul {
    display: inline-flex;
    list-style-type: none;
    padding-left: 0em;
    width: 100%;
    margin-bottom: 0px;
}


/* TODO: REFACTOR MOVE fileAssist TO COMPONENT */
.fileAssist { 
    background-color: rgba(0, 0, 0, 0.9);
    border-radius: 1.5em;
    box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
    position: absolute;
    color: whitesmoke;
    z-index: 1000;
}

.fileAssist ul {
    display: block;
    list-style-type: none;
    padding-left: 0em;
}

.fileAssist ul li {
    padding-left: 1em;
    padding-right: 1em;
    cursor: pointer;
    border-radius: 1em;
}

.fileAssist .fileAssistText {
    color: yellow;
    font-weight: bold;
}

.fileAssist ul li.selected {
    border: 1px solid whitesmoke;
}
</style>