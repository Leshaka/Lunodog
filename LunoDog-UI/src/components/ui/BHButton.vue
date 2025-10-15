<template>
<button :class="{large: large}">
  <img v-if="iconLeft" :src="iconLeft" class="left"/>
  <div>
    <span>{{ text }}</span>
  </div>
  <img v-if="iconRight" :src="iconRight" class="right"/>
</button>
</template>

<script>
export default {
  props: {
    text: {type: String, required: true},
    iconLeft: {type: String, requeired: false},
    iconRight: {type: String, required: false},
    large: {type: Boolean, requeired: false, default: false}
  }
}
</script>

<style lang="scss" scoped>
button {
  all: unset;
  font-family: os-medium;
  display: flex;
  align-items: center;
  padding: 6px;
  color: var(--c-btn-text);
  background-color: var(--c-btn);
  min-width: 64px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  user-select: none;
  box-shadow: 2px 2px var(--c-input);
}

img {
  height: 16px;
}

div {
  flex: 1 1 auto;
  margin: 0 6px 0 6px;
  display: flex;
  justify-content: center;
}

img.left {
  margin-left: 6px;
}

button:disabled {
  cursor: not-allowed;
  filter: grayscale(60%) contrast(50%);
}

button:not([disabled]):hover {
  filter: brightness(115%);
}

button.large {
  padding: 18px 6px 18px 6px;
  min-width: 96px;
  box-shadow: 4px 4px var(--c-input);
  border-radius: 8px;
}

button.large img.left {
  height: 24px;
}

button.gray {
  color: var(--c-text0);
  background-color: var(--c-sf1);
}

button.gray:hover {
  background-color: var(--c-sf2);
  color: var(--c-text1);
}




</style>