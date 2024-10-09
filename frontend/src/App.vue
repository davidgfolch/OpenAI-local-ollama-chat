<script>
import ChatHeader from './components/ChatHeader.vue';
import ChatContainer from './components/ChatContainer.vue';

export default {
  components: {
    ChatHeader,
    ChatContainer
  },
  data() {
    return {
      messages: [{
        'q': '<p>Hola AI!</p>',
        'a': '<p>Hola! en que puedo ayudarte?</p>'
      }]
    }
  }
}
</script>

<template>
  <ChatHeader msg="OpenAi local Ollama chat" />
  <ChatContainer :initial-messages="messages" />
</template>

<style>
@import url('https://fonts.googleapis.com/css?family=Lato');
* {
	box-sizing: border-box;
}

body {
	background: url('assets/background1.png');
  background-repeat: no-repeat;
	background-size: cover;
  background-attachment: fixed;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	min-height: 100vh;
	font-family: 'Lato', sans-serif;
	margin: 0 0 50px;
}
</style>