<script lang="ts" setup>
import { ref, defineExpose, defineEmits, onMounted } from 'vue';
import { insertAtCursor } from './utils';
import { apiClient } from './ApiClient';

const props = defineProps<{ inputElement: HTMLTextAreaElement | HTMLInputElement }>()

const emit = defineEmits(['errorReset', 'handleError']);
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

const shortCuts = (e: KeyboardEvent) => {
    var key = e.key;
    // console.log("key=" + key + " e.ctrlKey=" + e.ctrlKey);
    if (key == '@') {
        filesAvailableFiltered.value = filesAvailable;
        const rect = props.inputElement.getBoundingClientRect();
        fileAssistTop.value = rect.height;
        fileAssistLeft.value = rect.width / 3;
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
            e.preventDefault();
            return selectFile(fileSelectedIndex);
        } else if (key == 'ArrowUp' || key == 'ArrowLeft') fileSelectedMove(-1);
        else if (key == 'ArrowDown' || key == 'ArrowRight') fileSelectedMove(1);
        else {
            const matches = key.match(/[.a-zA-Z0-9_\-/]{1,1}/gi)
            if (matches != null && matches.length == 1) {
                fileAssistText += key;
                filterFilesAvailable();
                return
            }
            e.preventDefault();
        }
    }
}
const fileSelectedMove = (move: number) => {
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
/**
 * Filter files list by entered text via regular expression
 * First: try to filter by exact text match
 * Second: try to filter by matching text chunks obtained from the text
 */
const filterFilesAvailable = () => {
    const text = fileAssistText.toLowerCase().substring(1);
    const textChunks = text.match(/[a-z]+/ig)
    const textRegex = new RegExp('(' + text + ')', 'ig');
    const textChunksRegex = textChunks ? new RegExp('(' + textChunks.join('.+') + ')', 'gi') : textRegex;
    const filtered1 = filesAvailable.filter(f => f.toLowerCase().indexOf(text) != -1)
        .map(f => f.replace(textRegex, '<span style="color: yellow">$1</span>'))
    const filtered2 = filtered1.length > 10 ? [] : filesAvailable.filter(f => {
        const matches = f.match(textChunksRegex)
        return (matches != null && matches.length == 1);
    }).map(f => f.replace(textChunksRegex, '<span style="color: yellow">$1</span>'))
    const filtered = filtered1.concat(filtered2);
    if (fileSelectedIndex >= filtered.length) fileSelectedIndex = filtered.length
    filesAvailableFilteredUpdateView(filtered);
}
const filesAvailableFilteredUpdateView = (filtered) => {
    filesAvailableFiltered.value = [];
    filesAvailableFiltered.value = filtered;
}
const selectFile = (idx: number) => {
    const fileName = fileAssistText
    const offset = -fileName.length
    console.log("selectFile fileName=" + fileName + ", offset=" + offset);
    const fullFileNamePath = filesAvailableFiltered.value[idx].replace('<span style="color: yellow">', '').replace('</span>', '');
    showFileAssist.value = false;
    return insertAtCursor(props.inputElement, ' @' + fullFileNamePath + ' ', offset);
}

defineExpose({ shortCuts, loadFiles })
onMounted(() => {loadFiles()})
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