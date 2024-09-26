<script>
export default {
	props: ["msg"]
}
</script>

<template>
	<h2>{{ msg }}</h2>
</template>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h2 {
	text-shadow: 1px 1px 2px rgba(0, 0, 0, 1);
	color: #fff;
	letter-spacing: 1px;
	text-transform: uppercase;
	text-align: center;
	background-color: rgba(0, 0, 0, 0.4);
	border-radius: 25px;
	box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.7);
	/* overflow: hidden; */
	padding: 15px;
}
</style>
