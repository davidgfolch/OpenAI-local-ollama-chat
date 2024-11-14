<script lang="ts" setup>
import { ref, onMounted, onUnmounted, defineExpose, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';
import ChatHelp from './ChatHelp.vue';
import ChatError from './ChatError.vue';
import ChatOptions from './ChatOptions.vue';
import { loadHistoryMapper, answerMetadataMapper, createBodyParams, highLightCode } from './ChatContainerUtil';
import { apiClient, processDownloadProgress, AXIOS_CONTROLLER_ABORT_MSG } from './ApiClient';
import { checkUnclosedCodeBlockMd } from './utils';
import { showdown } from "vue-showdown";

// Vars
const mdConverter = new showdown.Converter();
let apiCliController = null; //https://axios-http.com/docs/cancellation
let currentChunkId = '';
let automaticScrollDown = false;
let streamTimeStart = Date.now();
// Reactive data
const user = ref('localUser');
const loading = ref(false);
const question = ref('');
const messages = ref([]);
const scrollDiv = ref(null);
const chatError = ref(null);
const chatOptions = ref();
// Methods
const errorReset = () => chatError.value.reset();
var scrollDownEnabled = true;
var lastScroll = 0;
let cancelled = false
const scrollDownChat = () => {
  if (scrollDownEnabled) {
    if (scrollDiv.value)
      nextTick().then(() => {
        automaticScrollDown = true
        scrollDiv.value.scrollIntoView({ behavior: 'smooth' })
        automaticScrollDown = false
      })
    else console.error("Can't scrollIntoView null element!");
  }
}
const loadHistory = () => {
  if (!chatOptions.value.history) {
    handleError('Could not load history messages, select current history in options fields.')
    return
  }
  loading.value = true
  apiClient.get(`/api/v1/chat/history/${user.value}/${chatOptions.value.history}`).then(res => {
    messages.value = []
    if (res.data.response.length === 0) {
      return
    }
    loadHistoryMapper(res, (q: string, a: string, id: string, metadata: any) => {
      messagePush(q, a, id, metadata)
      scrollDownChat()
      highLightCode(id)
    })
  }).catch(handleError).finally(resetApiCall);
}
const mdToHtml = (msg: string) => mdConverter.makeHtml(checkUnclosedCodeBlockMd(msg));
const messagePush = (q: string, a: string, id: string, metadata: any) =>
  messages.value.push({ q: mdToHtml(q), a: mdToHtml(a), id: id, metadata: metadata });
const setAnswer = (answer: string, resetQuestion: Boolean = false) => {
  automaticScrollDown = true
  let res: any = answerMetadataMapper(answer, streamTimeStart)
  currentChunkId = res.currentChunkId
  messagePush(question.value, res.text, currentChunkId, res.metadataJson)
  if (resetQuestion) question.value = ''
  highLightCode(currentChunkId);
  scrollDownChat()
}
const handleError = (error: Error | String) => chatError.value.showError(error);
const resetApiCall = () => {
  scrollDownEnabled = true;
  loading.value = false;
  scrollDownChat()
}
const errorCallbackFnc = () => {
  messages.value.pop();
  handleError("Stream chat response was empty.  Did you start ollama service?  Checkout backend logs.");
}
const streamMultiple = async (q: string) => {
  const variable = q.match(/\{([a-z]+)\}/i)[1];
  const matcher = q.match(variable + ' *= *(.*)')
  if (matcher == null) {
    handleError('Invalid variable value format: variable found ' + variable + ', but did not found ´' + variable + '´=x,y,z')
    return
  }
  const values = matcher[1].split(',')
  const regex = new RegExp(" *" + variable + " *= *.+\n?", 'igm');
  q = q.replaceAll(regex, '')
  streamTrigger(q, variable, values.reverse())
}
const streamTrigger = (q: string, variable: string, values: string[]) => {
  if (cancelled) {
    setTimeout(() => cancelled = false, 2000)
    return
  }
  if (!loading.value) {
    const value = values[values.length - 1]
    values.pop()
    const regex = new RegExp("\{" + variable + "\}", 'igm');
    const cq = q.replaceAll(regex, value.trim())
    stream(cq)
  }
  if (values.length > 0) setTimeout(() => streamTrigger(q, variable, values), 2000)
}
const stream = async (q: string) => {
  cancelled = false
  question.value = q
  if (question.value.trim() == '') return
  loading.value = true
  currentChunkId = ''
  streamTimeStart = Date.now()
  errorReset()
  setAnswer('<p>Waiting for response...</p>')
  scrollDownEnabled = true
  apiCliController = new AbortController()
  apiClient.post('/api/v1/chat-stream', createBodyParams(chatOptions.value, question.value, user.value), {
    signal: apiCliController.signal,
    onDownloadProgress: (progressEvent) =>
      processDownloadProgress(progressEvent,
        () => errorCallbackFnc(),
        (dataChunk: string) => {
          messages.value.pop()
          setAnswer(dataChunk)
        })
  }).then(() => question.value = '')
    .catch(e => {
      cancelled = e == AXIOS_CONTROLLER_ABORT_MSG
      if (!cancelled) messages.value.pop()
      handleError(cancelled ? 'Stream request cancelled by user' : e)
    }).finally(() => {
      if (!cancelled && messages.value.length > 0 && messages.value[messages.value.length - 1]['a'] == '<p>Waiting for response...</p>')
        errorCallbackFnc() //TODO: chrome don't pass through ApiClient.ts -> processDownloadProgress() -> progressEvent.loaded == 0
      resetApiCall()
    })
};
const messagesReset = () => {
  messages.value = []
  nextTick(() => loadHistory())
}
const deleteMessage = (index: number) => {
  errorReset()
  apiClient.get(`/api/v1/chat/delete/${user.value}/${chatOptions.value.history}/${index}`)
    .then(() => messages.value.splice(index, 1))
    .catch(e => {
      handleError(e)
      scrollDownChat()
    })
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
const handleScroll = (event: UIEvent) => {
  const viewHeight = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)
  const scroll = document.body.scrollTop ? document.body.scrollTop : document.documentElement.scrollTop
  // console.log('handleScroll scroll='+scroll+' scrollHeight='+document.body.scrollHeight+' scrollTop='+document.body.scrollTop+' clientHeight='+document.body.clientHeight+
  //   'viewHeight='+viewHeight+' calculation '+(document.body.scrollHeight-scroll-viewHeight)
  // )
  const scrolledBottom = Math.abs(document.body.scrollHeight - document.body.scrollTop - document.body.clientHeight) < 1
  // if (scroll < lastScroll)
  //   scrollDownEnabled = false
  // else if (document.body.scrollHeight-scroll-viewHeight < viewHeight/2) scrollDownEnabled = true
  scrollDownEnabled = document.body.scrollHeight - scroll - viewHeight < viewHeight / 2
  lastScroll = scroll
}
onMounted(() => {
  chatOptions.value.loadHistories()
    .then(() => nextTick(() => {
      loadHistory()
    }))
  window.addEventListener('scroll', handleScroll)
});
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
defineExpose({ errorReset, setAnswer, messagesReset, handleError, scrollDownChat, stream, streamMultiple, cancelStream, deleteMessage });
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
    @stream="q => stream(q)" @stream-multiple="q => streamMultiple(q)" @load-history="loadHistory" ref="chatOptions" />
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
