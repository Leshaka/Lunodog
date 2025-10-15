<template>
  <div class="layout">
    <div class="title"> {{ errorStore.title }} </div>
    <div class="body"> {{ errorStore.body }} </div>
    <BHButton @click="$router.back()" text="Go back"/>
  </div>
</template>

<script>
import { useErrorStore } from '@/stores/error'
import BHButton from '@/components/ui/BHButton.vue';


export default {
  components: { BHButton },
  data() {
    return {
      errorStore: useErrorStore(),
    }
  }
}

</script>

<style scoped lang="scss">
.layout {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 32px;
  color: var(--c-text0);
  font-size: 20px;
  font-family: "barlow-medium";

  min-width: 100%;
  min-height: 100vh;

  .title {
    color: var(--c-text-red);
    font-size: 32px;
    font-family: os-bold;
  }

  .body {
    white-space: pre;
  }
}



</style>