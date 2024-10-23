<script setup>
// import { onMounted, ref } from 'vue';
import ChatHeader from './components/ChatHeader.vue';
import ChatContainer from './components/ChatContainer.vue';
</script>

<template>
	<ChatHeader msg="OpenAi local Ollama chat" />
	<ChatContainer />
</template>

<style>
@import url('https://fonts.googleapis.com/css?family=Lato');

* {
	box-sizing: border-box;
}

body {
	background: url('assets/background.webp');
	background-repeat: no-repeat;
	background-size: cover;
	background-attachment: fixed;
	background-color: black;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	min-height: 100vh;
	font-family: 'Lato', sans-serif;
}
</style>
