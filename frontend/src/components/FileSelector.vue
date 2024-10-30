<script setup>
import { ref, defineExpose, defineEmits, onMounted } from 'vue';
import { insertAtCursor } from './utils';
import { apiClient } from './ApiClient.js';

const emit = defineEmits(['errorReset', 'handleError']);
const question = ref('')
const showFileAssist = ref(false)
let fileAssistText = ''
let fileSelectedIndex = 0;
const fileAssistLeft = ref(0)
const fileAssistTop = ref(0)
let filesAvailable = []
const filesAvailableFiltered = ref([])

const loadFiles = () => {
    emit('errorReset');
    apiClient.get('/api/v1/files')
        .then(res => filesAvailable = res.data.response)
        .catch(e => emit('handleError', e));
}

const shortCuts = (e) => {
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
        else if (key == 'Enter') {
            selectFile(fileSelectedIndex);
            e.preventDefault();
        } else if (key == 'ArrowUp' || key == 'ArrowLeft') fileSelectedMove(-1);
        else if (key == 'ArrowDown' || key == 'ArrowRight') fileSelectedMove(1);
        else {
            const matches = key.match(/[a-zA-Z0-9_\-/]{1,1}/gi)
            if (matches!=null && matches.length == 1) {
                fileAssistText += key;
                filterFilesAvailable();
                return
            }
            e.preventDefault();
        }
    }
}
const fileSelectedMove = (move) => {
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
const filterFilesAvailable = () => {
    const text = fileAssistText.toLowerCase().substring(1);
    const regex = new RegExp('(' + text + ')', 'ig');
    const filtered = filesAvailable
        .filter(f => f.toLowerCase().indexOf(text) != -1)
        .map(f => f.replace(regex, '<span style="color: yellow">$1</span>'));
    if (fileSelectedIndex >= filtered.length) fileSelectedIndex = filtered.length
    filesAvailableFilteredUpdateView(filtered);
}
const filesAvailableFilteredUpdateView = (filtered) => {
    filesAvailableFiltered.value = [];
    filesAvailableFiltered.value = filtered;
}
const selectFile = (idx) => {
    const fileName = filesAvailableFiltered.value[idx].replace('<span style="color: yellow">', '').replace('</span>', '');
    const offset = -fileName.length
    console.log("selectFile fileName=" + fileName + ", offset=" + offset);
    question.value = insertAtCursor(document.getElementById("textarea-question"), ' @' + fileName + ' ', offset);
    showFileAssist.value = false;
}

defineExpose({ shortCuts })
onMounted(() => loadFiles())
</script>

<template>
    <div v-if="showFileAssist" class="fileAssist"
        :style="'left: ' + fileAssistLeft + 'px; top: ' + fileAssistTop + 'px;'">
        <ul>
            <li v-for="(file, idx) in filesAvailableFiltered" :key="idx" @click="selectFile(idx)" v-html="file"
                :class="fileSelectedIndex == idx ? 'selected' : ''"></li>
        </ul>
    </div>
</template>

<!-- lang="scss" -->
<style scoped>
.fileAssist {
    background-color: rgba(0, 0, 0, 0.9);
    border-radius: 1.5em;
    box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
    position: absolute;
    color: whitesmoke;
    z-index: 1000;
    max-height: 10em;
    overflow-y: scroll;
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