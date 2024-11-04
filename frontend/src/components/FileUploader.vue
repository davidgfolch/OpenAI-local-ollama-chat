<script lang="ts" setup>
import { ref, defineEmits, defineExpose } from 'vue';
const emit = defineEmits(['filesUpload']);
const files = ref<File[]>([])
const showUploadButton = ref(true)
const showLoading = ref(false)
const loadedDivStyle = ref('')
let loaded = 0;
let total = 0;
let percentCompleted: number = 0;
const openDialog = (picker) => {
    const element = document.getElementById(picker);
    element.addEventListener("change", (event) => {
        // console.log("change event => event.target.files.length=" + event.target.files.length);
        const allFiles: Array<File> = event.target.files;
        const filteredFiles: Array<File> = []
        for (const file of allFiles) {
            if (!/(\/.git|\/node_modules\/|\/assets\/|\/public\/|\/uploads\/|\/__pycache__|\/.pytest_cache|\/\.[a-zA-Z0-9-_])/.test(file.webkitRelativePath)) { // includes file name
                // console.log("file=>" + file.webkitRelativePath);
                filteredFiles.push(file);
                showUploadButton.value = true;
            }
        }
        event.target.files = makeFileList(filteredFiles);
        files.value = filteredFiles
    }, false);
    element.click();
}
const makeFileList = (files: Array<File>) => {
    const reducer = (dataTransfer: DataTransfer, file: File) => {
        dataTransfer.items.add(file);
        return dataTransfer;
    }
    return files.reduce(reducer, new DataTransfer()).files;
}
const removeFile = (index: number) => {
    files.value.splice(index, 1);
}

const addFilesToFormData = () => {
    showLoading.value = true
    const formData = new FormData();
    // console.log("addFiles files.length=" + files.value.length);
    files.value.forEach(f => {
        // console.log("file=" + JSON.stringify(f));
        formData.append(String(f), f);
    });
    showLoading.value = false
    // console.log("formData=" + formData);
    return formData;
}
const filesUpload = () => {
    showUploadButton.value = false;
    emit('filesUpload', addFilesToFormData());
}
const setShowUploadButton = (value) => showUploadButton.value = value;
const showProgress = (pLoaded: number, pTotal: number) => {
    loaded = pLoaded
    total = pTotal
    percentCompleted = Math.round((loaded * 100) / total)
    if (pLoaded == pTotal) {
        files.value = [];
    }
    loadedDivStyle.value = 'width: ' + percentCompleted + '%;';
}
const getFileSize = (size: number): string => {
    if (size > 0) {
        if (size > 1000000) return String(size / 1000000).split('.')[0] + 'mb';
        if (size > 1000) return String(size / 1000).split('.')[0] + 'kb';
        return String(size) + 'b';
    }
    return '0';
}
const getFileSizeToColor = (file: File) => {
    const size = getFileSize(file.size);
    const sizeNum = ((Number(size.replaceAll(/[a-z]+/ig, '')) * 100 / 1000) + 155).toFixed(0);
    let res = '';
    if (size.indexOf('mb') != -1) //red
        res = sizeNum + ',0,0';
    else if (size.indexOf('kb') != -1) //yellow
        res = sizeNum + ',' + sizeNum + ',0';
    else res = '0,' + sizeNum + ',0'; //green
    return 'rgba(' + res + ',40);';
}

defineExpose({ openDialog, setShowUploadButton, showProgress, removeFile });
</script>

<template>
    <div style="clear:both" class="container">
        <!-- https://web.dev/patterns/files/open-a-directory#js
            https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/webkitdirectory -->
        <input type="file" id="file-picker" class="text_input" multiple />
        <input type="file" webkitdirectory id="folder-picker" class="text_input" multiple accept="application/text" />
        <div v-if="total != 0" class="progress-wrapper">
            <div class="progress-bar">
                <div class="progress-bar-fill" :style="loadedDivStyle">{{ percentCompleted + '% (' + getFileSize(loaded) + ') uploaded' }}</div>
                {{ getFileSize(total) }} total
            </div>
        </div>
        <div v-if="showLoading">
            <slot name="loading"></slot>
        </div>
        <ul v-if="files.length > 0">
            <li v-if="showUploadButton">
                <button @click="filesUpload" class="upload">Upload files</button>
            </li>
            <li v-else class="uploadedFiles">Uploaded files:&nbsp;</li>
            <li v-for="(file, index) in files" :key="index"
                :title="file.webkitRelativePath + ' (' + getFileSize(file.size) + ')->' + index"
                :style="'background-color: ' + getFileSizeToColor(file)">
                <slot :removeFile="removeFile" :index="index" name="removeFile">
                    <button @click="removeFile(index)" class="close">(defaultSlot)X</button>
                </slot>
                {{ file.name }}
            </li>
        </ul>
    </div>
</template>

<style scoped>
.container {
  background-color: rgba(0, 0, 0, 0.4);
  border-radius: 1.5em;
  box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
  position: relative;
  margin-bottom: 1.5em;
}

ul {
    max-width: 90%;
    padding: 0em;
    margin-top: 0px;
}

li {
    font-size: small;
    color: rgb(0, 0, 0);
    border-radius: 0.5em;
    padding: 0em 0.2em 0.1em 0.2em;
    position: relative;
    margin-left: 0.5em;
    margin-bottom: 0.2em;
    display: inline-block;
    text-align: center;
}

li.uploadedFiles {
    padding: 0.2em 0.2em 0.2em 0.2em;
}

.close {
    font-size: xx-small;
    background-color: rgb(200, 200, 200);
    color: black;
    border-radius: 0.5em;
    padding: 0em 0.2em 0.1em 0.2em;
    margin-left: 0.3em;
    position: relative;
    top: -0.6em;
}

.upload {
    font-size: small;
    background-color: rgb(200, 200, 200);
    color: black;
    border-radius: 0.5em;
    padding: 0em 0.2em 0.1em 0.2em;
    position: relative;
    top: -0.2em;
}

input[type=file] {
    display: none;
}

.progress-wrapper {
    width: 100%;
}

.progress-bar {
    position: absolute;
    width: 95%;
    font-size: small;
    background-color: rgb(200, 200, 200);
    color: black;
    border-radius: 0.5em;
    padding: 0em 0.2em 0.1em 0em;
    text-align: right;
    overflow: hidden;
}

.progress-bar-fill {
    position: absolute;
    background-color: rgb(0, 150, 0);
    color: whitesmoke;
    border-radius: 0.5em;
    padding: 0em 0.2em 0.1em 0.2em;
    margin: 0px;
    display: block;
    text-align: left;
    transition: width 500ms ease-in-out;
}

</style>