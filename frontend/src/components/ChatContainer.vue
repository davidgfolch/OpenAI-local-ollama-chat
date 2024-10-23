<script setup>
import { ref, onMounted, defineExpose, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatHelp from './ChatHelp.vue';
import ChatError from './ChatError.vue';
import ChatOptions from './ChatOptions.vue';
import { apiClient, processDownloadProgress, AXIOS_CONTROLLER_ABORT_MSG } from './ApiClient.js';
import hljs from 'highlight.js';
import { checkUnclosedCodeBlockMd, scrollDown } from './utils.js';
import { showdown } from "vue-showdown";

// Vars
const mdConverter = new showdown.Converter();
let apiCliController = null; //https://axios-http.com/docs/cancellation
let currentChunkId = '';
let now = 0;
let streamTimeStart = Date.now();
// Reactive data
const user = ref('localUser');
const loading = ref(false);
const question = ref('');
const messages = ref([]);
const scrollDiv = ref(null);
const chatError = ref('');
const chatOptions = ref();
// Methods
const highLightCode = () => nextTick().then(() => hljs.highlightAll());
const errorReset = () => chatError.value.reset();
var scrollDownEnabled = true;
const scrollDownChat = () => { if (scrollDownEnabled) scrollDown(scrollDiv.value); }
const loadHistory = () => {
  let q = null, a = null, id = null, metadata = null;
  loading.value = true;
  apiClient.get(`/api/v1/chat/${user.value}`).then(res => {
    if (res.data.response.length === 0) {
      messages.value = [];
      return;
    }
    res.data.response.forEach((msg) => {
      if (msg.q) q = msg.q;
      if (msg.a) {
        a = msg.a;
        metadata = msg.metadata;
        id = msg.id;
      }
      if (a != null && q != null) {
        messagePush(q, a, id, JSON.parse(metadata));
        scrollDownChat()
        highLightCode();
        q = null, a = null;
      }
    });
  }).catch(handleError).finally(resetApiCall);
};
const mdToHtml = (msg) => mdConverter.makeHtml(checkUnclosedCodeBlockMd(msg));
const messagePush = (q, a, id, metadata) => messages.value.push({q: mdToHtml(q), a: mdToHtml(a), id: id, metadata: metadata});
const setAnswer = (answer, resetQuestion) => {
  const arr = answer.split("#|S|E|P#");
  if (arr.length > 1) {
    currentChunkId = arr[0]
    const modelName = arr[1]
    const langchainChat = arr[2]
    const text = arr[3]
    const metadataStr = arr[4]
    now = Date.now();
    let metadata = arr.length > 4 ? metadataStr : '{"total_duration": '+(now-streamTimeStart)+'}'
    metadata = JSON.parse(metadata)
    metadata.total_duration = now-streamTimeStart;
    metadata.model = modelName;
    metadata.langchainChat = langchainChat;
    messagePush(question.value, text, currentChunkId, metadata);
  } else {
    messagePush(question.value, answer, '', '');
  }
  if (resetQuestion) question.value = '';
  scrollDownChat()
  highLightCode();
};
const handleError = (error) => chatError.value.show(error);
const resetApiCall = () => {
  scrollDownEnabled = true;
  loading.value = false;
  scrollDownChat()
};
const errorCallbackFnc = () => {
  messages.value.pop();
  handleError("Stream chat response was empty.  Did you start ollama service?  Checkout backend logs.");
}
const stream = async (q) => {
  question.value = q
  if (question.value.trim() == '') return
  loading.value = true;
  currentChunkId = '';
  streamTimeStart = Date.now();
  now = Date.now();
  errorReset();
  setAnswer('<p>Waiting for response...</p>');
  scrollDownEnabled = false;
  const options = chatOptions.value;
  const body = { model: options.model, user: user.value, question: question.value, history: options.history, ability: options.ability };
  apiCliController = new AbortController();
  let cancelled = false;
  apiClient.post('/api/v1/chat-stream', body, {
    signal: apiCliController.signal,
    onDownloadProgress: (progressEvent) =>
      processDownloadProgress(progressEvent,
        () => errorCallbackFnc(),
        (dataChunk) => {
          if (dataChunk != '') {
            messages.value.pop();
            setAnswer(dataChunk);
          }
        })
  }).then(() => question.value = '')
    .catch(e => {
      cancelled = e == AXIOS_CONTROLLER_ABORT_MSG;
      if (!cancelled)
        messages.value.pop()
      let err = cancelled ? 'Stream request cancelled by user' : e;
      handleError(err);
    }).finally(() => {
      if (!cancelled && messages.value.length > 0 && messages.value[messages.value.length - 1]['a'] == '<p>Waiting for response...</p>')
        errorCallbackFnc(); //TODO: chrome don't pass through ApiClient.js -> processDownloadProgress() -> progressEvent.loaded == 0
      resetApiCall();
    });
};
const messagesReset = () => {
  messages.value = [];
  nextTick(() => loadHistory());
};
const deleteMessage = (index) => {
  errorReset();
  apiClient.get(`/api/v1/chat/delete/${user.value}/${index}`)
    .then(() => messages.value.splice(index, 1))
    .catch(e => {
      handleError(e);
      scrollDownChat();
    });
}
const cancelStream = () => {
  errorReset();
  apiClient.get(`/api/v1/chat/cancel/${user.value}`)
    .then(() => apiCliController.abort())
    .catch(e => {
      handleError(e);
      scrollDownChat();
    });
}

onMounted(() => loadHistory());
defineExpose({ errorReset, setAnswer, messagesReset, handleError, scrollDownChat, stream, cancelStream, deleteMessage });
</script>


<template>
  <div class="chat-container">
    <ul class="chat">
      <ChatMessage v-for="(msg, index) in messages" :key="index" :msg="msg" :total="messages.length" :index="index"
        :loading="loading" @cancel-stream="cancelStream()" @delete-message="deleteMessage(index)" />
      <Transition name="verticalExpand">
        <ChatHelp v-if="messages.length == 0 || chatOptions.showHelp" />
      </Transition>
      <ChatError ref="chatError" />
    </ul>
  </div>
  <ChatOptions :question="question" :loading="loading" :user="user" :view-settings="false"
    :enable-delete="messages.length > 0" @error-reset="errorReset()" @handle-error="e => handleError(e)"
    @set-answer="a => setAnswer(a)" @messages-reset="messagesReset()" @scroll-down-chat="scrollDownChat"
    @stream="q => stream(q)" ref="chatOptions" />
  <div ref="scrollDiv" class="scrollDiv"></div>
</template>


<style>
@import url("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/dark.min.css");

.verticalExpand-enter-active {
  animation: verticalExpand-in 0.5s;
}

.verticalExpand-leave-active {
  animation: verticalExpand-in 0s reverse;
}

@keyframes verticalExpand-in {
  0% {
    transform: scaleY(0);
  }

  /* 50% {
    transform: scaleY(1.25);
  } */
  100% {
    transform: scaleY(1);
  }
}

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
</style>
