<script>
import { RouterView } from 'vue-router'

export default {
  mounted() {
    let theme = localStorage.getItem('theme');
    if (!theme) {
      const wantDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      theme =  wantDark ? 'dark' : 'dark';
    };
    document.documentElement.setAttribute('theme', theme);
  }
}
</script>

<template>
<RouterView/>
</template>