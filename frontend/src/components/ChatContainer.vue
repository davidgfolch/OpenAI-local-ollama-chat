<script setup>
import { ref, onMounted, defineProps, defineExpose, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatError from './ChatError.vue';
import ChatOptions from './ChatOptions.vue';
import {apiClient, processDownloadProgress} from './ApiClient.js';
import hljs from 'highlight.js';
import { checkUnclosedCodeBlockMd, scrollDown } from './utils.js';
import { showdown } from "vue-showdown";

// Props
const props = defineProps({
  initialMessages: {
    type: Array,
    default: () => []
  }
});
const mdConverter = new showdown.Converter();

// Reactive data
const user = ref('localUser');
const loading = ref(false);
const question = ref('');
const messages = ref([]);
// Refs
const scrollDiv = ref(null);
const chatError = ref('');
const chatOptions = ref();
// Methods
const highLightCode = () => nextTick().then(() => hljs.highlightAll());
const errorReset = () => chatError.value.reset();
var scrollDownEnabled = true;
const scrollDownChat = () => { if (scrollDownEnabled) scrollDown(scrollDiv.value); }
const loadHistory = () => {
  console.log("loadHistory");
  let q = null, a = null;
  loading.value = true;
  apiClient.get(`/api/v1/chat/${user.value}`).then(res => {
    if (res.data.response.length === 0) {
      messages.value = props.initialMessages;
      return;
    }
    res.data.response.forEach((msg) => {
      if (msg.q) q = msg.q;
      if (msg.a) a = mdConverter.makeHtml(checkUnclosedCodeBlockMd(msg.a));
      if (a != null && q != null) {
        messages.value.push({ q, a });
        scrollDownChat()
        highLightCode();
        q = null, a = null;
      }
    });
  }).catch(handleError).finally(resetApiCall);
};
const setAnswer = (answer, resetQuestion) => {
  messages.value.push({ q: '<p>' + question.value + '</p>', a: mdConverter.makeHtml(answer) });
  if (resetQuestion) question.value = '';
  scrollDownChat()
  highLightCode();
};
const handleError = (error) => {
  console.log("handleError error=" + error)
  chatError.value.show(error);
};
const resetApiCall = () => {
  scrollDownEnabled = true;
  loading.value = false;
  scrollDownChat()
};
const errorCallbackFnc = () => {
  loadHistory();
  handleError("Stream chat response was empty.  Did you start ollama service?  Checkout backend logs.");
}
const useStream = true
const invoke = async (q) => {
  question.value = q
  if (question.value.trim() == '') return
  loading.value = true;
  errorReset();
  scrollDownEnabled = true;
  setAnswer('<p>Waiting for response...</p>');
  scrollDownEnabled = false;
  const options = chatOptions.value;
  const body = { model: options.model, user: user.value, question: question.value, history: options.history, ability: options.ability };
  const url = useStream ? '/api/v1/chat-stream' : '/api/v1/chat'
  apiClient.post(url, body, {
    onDownloadProgress: (progressEvent) =>
      processDownloadProgress(progressEvent,
        () => errorCallbackFnc(),
        (dataChunk) => {
          dataChunk = checkUnclosedCodeBlockMd(dataChunk)
          messages.value.pop();
          setAnswer(dataChunk);
        })
  }).then(() => {
    question.value = ''
  }).catch(e => {
    console.log("catch e=" + e)
    messages.value.pop()
    handleError(e);
  }).finally(() => {
    if (messages.value[messages.value.length - 1]['a'] == '<p>Waiting for response...</p>')
      errorCallbackFnc(); //TODO: chrome don't pass through ApiClient.js -> processDownloadProgress() -> progressEvent.loaded == 0
    resetApiCall();
  });
  // https://stackoverflow.com/questions/72781074/piping-the-response-into-a-variable-using-streams-axios-node-js
  // axios.get responseType: 'stream' https://stackoverflow.com/questions/71534322/http-stream-using-axios-node-js
};


const messagesReset = () => {
  messages.value = [];
  console.log("messagesReset");
  nextTick(() => loadHistory());
};
onMounted(() => { // Lifecycle hook
  loadHistory();
});
defineExpose({ errorReset, setAnswer, messagesReset, handleError, scrollDownChat, invoke });
</script>


<template>
  <div class="chat-container">
    <ul class="chat">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :msg="msg" :total="messages.length" :index="index"
        :loading="loading" />
      <ChatError ref="chatError" />
    </ul>
  </div>
  <ChatOptions :question="question" :view-settings="false" :user="user" :loading="loading" @error-reset="errorReset()"
    @handle-error="e => handleError(e)" @set-answer="a => setAnswer(a)" @messages-reset="messagesReset()"
    @scroll-down-chat="scrollDownChat" @invoke="q => invoke(q)" ref="chatOptions" />
  <div ref="scrollDiv" class="scrollDiv"></div>
</template>


<style>
@import url("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/dark.min.css");

.chat-container {
  background-color: rgba(0, 0, 0, 0.4);
  border-radius: 1.5em;
  box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
  overflow: hidden;
  padding: 1em;
  position: relative;
  min-width: 10em;
  margin-left: 2em;
  margin-right: 2em;
}

.chat {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.scrollDiv {
  padding: 0;
  margin: 0;
}

.optionIcon {
  border-radius: 50%;
  box-shadow: 0px 0px 10px 5px rgba(26, 21, 21, 0.7);
  object-fit: cover;
  position: relative;
  float: right;
  width: 3em;
  height: 3em;
}
</style>
