<script lang="ts" setup>
import { onMounted, ref, defineProps, defineEmits, defineExpose } from 'vue';
import { apiClient, openDownloadedFile } from './ApiClient';
import FileUploader from './FileUploader.vue'
import FileSelector from './FileSelector.vue'

const emit = defineEmits(['errorReset', 'setAnswer', 'messagesReset', 'scrollDownChat', 'handleError', 'stream', 'streamMultiple', 'loadHistory']);
// Props
const props = defineProps({
    user: String,
    loading: Boolean,
    enableDelete: Boolean
});
// Reactive data
const hideSettings = ref(true);
const history = ref('qwen2.5-coder-7b');
const histories = ref([]);
const models = ref([]);
const model = ref("");
const temperature = ref(0.7);
const ability = ref("Eres un asistente especializado en ingenieria de software.  Generas codigo de calidad siguiendo los principios de desarrollo de software (best practices) como: SOLID, Clean Code, YAGNI: you aint gonna need it, KISS: keep it simple stupid, DRY: don't repeat yourself");
// const question = ref(`Genera un ejemplo de código completo con {variable} en python.
const question = ref(`Genera ejemplos completos de código con {variable} en python.

variable=Django, Flask, NumPy, Pandas, Matplotlib, Scikit-learn, Requests, BeautifulSoup, Pygame, Cython, TensorFlow, Keras, PyTorch, OpenCV, scikit-image, Pillow, Sanic, FastAPI, Tornado, Twisted, cryptography, PyNaCl, OpenSSL, SSL/TLS, PyCrypto, Pycryptodome, Hashlib, HMAC, SHA-256, MD5, os, sys, pathlib, shutil, tempfile, filecmp, mimetypes, gzip, bz2, tarfile`);
const showHelp = ref(false)
const fileUploader = ref<InstanceType<typeof FileUploader> | null>(null);
const message = ref();
const fileSelector = ref<InstanceType<typeof FileSelector> | null>(null);

// Methods
const stream = () => {
    if (props.loading) return;
    if (question.value.match(/\{[a-z]+\}/i)) {
        emit('streamMultiple', question.value);
    } else {
        emit('stream', question.value);
    }
}
const deleteChat = () => {
    if (!props.enableDelete) return;
    emit('errorReset');
    apiClient.get(`/api/v1/chat/delete/${props.user}/${history.value}`)
        .then(() => emit('messagesReset'))
        .catch(e => emit('handleError', e));
}
const loadHistories = () => {
    const promise = apiClient.get(`/api/v1/chat/history/${props.user}`)
    promise.then(res => {
        if (res.data.response.length === 0) {
            histories.value = []
            return
        }
        histories.value = res.data.response
        if (!history.value && histories.value)
            history.value = histories.value[0]
    }).catch(e => emit('handleError', e))
    return promise
}
const loadHistory = () => {
    emit('loadHistory');
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
const filesUpload = (formData) => {
    emit('errorReset');
    let total = 0;
    apiClient.postForm('/api/v1/files/upload', formData, {
        onUploadProgress: function (e) {
            fileUploader.value.showProgress(e.loaded, e.total);
            total = e.total;
        }
    }).then(() => {
        fileUploader.value.showProgress(total, total);
        fileSelector.value.loadFiles();
    }).catch(e => {
        fileUploader.value.setShowUploadButton(true);
        emit('handleError', e);
        return false;
    });
}
const openDialog = (input: string) => fileUploader.value?.openDialog(input);
const shortCuts = (e: KeyboardEvent) => {
    if (e.ctrlKey && e.key == 'Enter') stream();
    else {
        const res = fileSelector.value.shortCuts(e);
        if (res) question.value = res;
    }
}
const exportHistory = () => {
    apiClient.get(`/api/v1/export/${props.user}/${history.value}`, {
        responseType: 'blob'  // important
    }).then(res => openDownloadedFile(res, `${props.user}_${history.value}.zip`))
        .catch(e => emit('handleError', e))
}

defineExpose({ model, temperature, ability, loadHistories, history, question, showHelp });
onMounted(() => getModels())
</script>

<template>
    <div class="options-container" style="margin-top: 1em;">
        <div>
            <div>
                <div class="container">
                    <ul>
                        <li style="width: 100%">
                            <textarea v-model="question" :rows="question.split('\n').length" :cols="80"
                                class="base-input textarea" placeholder="Message..." autofocus id="textarea-question"
                                ref="message" @keydown="shortCuts"></textarea>
                        </li>
                        <li>
                            <img src="../assets/chatgpt/send.webp" @click="stream"
                                :class="'sendIcon' + (loading ? ' disabled' : '')" alt="Ask AI (ctrl+enter)"
                                title="Ask AI (ctrl+enter)">
                        </li>
                    </ul>
                    <FileSelector ref="fileSelector" :inputElement="message" />
                    <FileUploader @filesUpload="form => filesUpload(form)" ref="fileUploader">
                        <template v-slot:loading>
                            <img class="logo loading" src="../assets/loading.gif" alt="Processing files"
                                title="Processing files" />
                        </template>
                        <template v-slot:removeFile="{ index }">
                            <img class="optionIconSmall" src="../assets/chatgpt/close.webp"
                                @click="fileUploader.removeFile(index)" alt="Remove file" title="Remove file">
                        </template>
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
        <div :hidden="hideSettings" style="clear: both; margin-top: 0.5em">
            <input type="text" class="input" v-model="ability"
                placeholder="Artificial intelligence system ability (describe any ability in natural language)"
                title="Artificial intelligence system ability (describe any ability in natural language)" />
        </div>
        <div :hidden="hideSettings">
            <select v-model="model" id="model" name="model" placeholder="Select model" title="Select model"
                v-if="models">
                <option value="">Select llm model...</option>
                <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
            </select>
            <input type="number" v-model="temperature" placeholder="Model temperature" title="Model temperature"
                size="2" />
            <input type="text" v-model="history" placeholder="Chat history" title="Current chat history"
                list="histories" />
            <datalist id="histories">
                <option v-for="h in histories" :key="h" :value="h">{{ h }}</option>
            </datalist>
            <button @click="loadHistory">Load history</button>
            <button @click="exportHistory">Export history...</button>
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

input,
textarea,
select {
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

select:not(.input),
input:not(.input) {
    margin-right: 1em;
}

.textarea {
    width: 99%;
}

textarea {
    margin-top: 0em;
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
    margin-top: 0px;
}
</style>