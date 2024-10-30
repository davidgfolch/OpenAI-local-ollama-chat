<script setup>
import { ref, defineEmits, defineExpose } from 'vue';
const emit = defineEmits(['filesUpload']);
const files = ref([])
const showUploadButton = ref(true)
let loaded = 0;
let total = 0;
let percentCompleted = 0;
const openDialog = (picker) => {
    const element = document.getElementById(picker);
    element.addEventListener("change", (event) => {
        // console.log("change event => event.target.files.length=" + event.target.files.length);
        const filteredFiles = []
        for (const file of event.target.files) {
            if (!/(\/.git|\/node_modules\/|\/assets\/|\/public\/|\/__pycache__|\/.pytest_cache|\/\.[a-zA-Z0-9-_])/.test(file.webkitRelativePath)) { // includes file name
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
const makeFileList = (files) => {
    const reducer = (dataTransfer, file) => {
        dataTransfer.items.add(file);
        return dataTransfer;
    }
    return files.reduce(reducer, new DataTransfer()).files;
}
const removeFile = (index) => {
    files.value.splice(index, 1);
}

const addFilesToFormData = () => {
    const formData = new FormData();
    // console.log("addFiles files.length=" + files.value.length);
    files.value.forEach(f => {
        // console.log("file=" + JSON.stringify(f));
        formData.append(f, f);
    });
    // console.log("formData=" + formData);
    return formData;
}
const filesUpload = () => {
    showUploadButton.value = false;
    emit('filesUpload', addFilesToFormData());
}
const setShowUploadButton = (value) => showUploadButton.value = value;
const showProgress = (pLoaded, pTotal) => {
    loaded = pLoaded
    total = pTotal
    percentCompleted = Math.round((loaded * 100) / total)
}
defineExpose({ openDialog, setShowUploadButton, showProgress });
</script>

<template>
    <div style="clear:both" class="container">
        <!-- https://web.dev/patterns/files/open-a-directory#js
            https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/webkitdirectory -->
        <input type="file" id="file-picker" class="text_input" multiple />
        <input type="file" webkitdirectory id="folder-picker" class="text_input" multiple accept="application/text" />
        <div v-if="total != 0" class="progress">
            <div class="loaded" :style="'with: ' + percentCompleted+'%'">{{ loaded }}</div>
            <div class="notLoaded">{{ total }}</div>
        </div>
        <ul v-if="files.length > 0">
            <li v-if="showUploadButton">
                <button @click="filesUpload" class="upload">Upload files</button>
            </li>
            <li v-else class="uploadedFiles">Uploaded files:&nbsp;</li>
            <li v-for="(file, index) in files" :key="index" :title="file.webkitRelativePath">
                <slot :removeFile="removeFile">
                    <button v-if="!hasSlot('default')" @click="removeFile(index)" class="close">X</button>
                </slot>
                {{ file.name }}
            </li>
        </ul>
    </div>
</template>

<style scoped>
ul {
    max-width: 90%;
    padding: 0em;
    margin-top: 0px;
}

li {
    font-size: small;
    color: rgb(200, 200, 200);
    background-color: rgba(100, 100, 0, 0.6);
    border-radius: 0.5em;
    box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
    padding: 0em 0.2em 0.1em 0.2em;
    position: relative;
    margin-left: 0.5em;
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

.progress {
    width: 100%;
    font-size: small;
    background-color: rgb(200, 200, 200);
    color: black;
    border-radius: 0.5em;
    padding: 0em 0em 0em 0em;
    display: inline-block;
}
.loaded {
    background-color: rgb(0, 150, 0);
    color: whitesmoke;
    border-radius: 0.5em;
    padding: 0em 0.2em 0.1em 0.2em;
    position: relative;
    float: left;
    margin: 0px;
}
.notLoaded {
    position: relative;
    float: right;
    padding: 0em 0.2em 0.1em 0.2em;
}
</style>