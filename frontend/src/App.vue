<style>
@import url('https://fonts.googleapis.com/css?family=Lato');
@import url('./assets/css.css');
</style>

<script>
import ChatHeader from './components/ChatHeader.vue';
import ChatContainer from './components/ChatContainer.vue';

export default {
  components: {
    ChatHeader,
    ChatContainer
  }
}
</script>

<template>
  <ChatHeader msg="Ask local Ollama"/>
  <ChatContainer/>
</template>

