<template>
  <div class="layout">
    <div class="error-message">
      <div class="title"> {{ errorStore.title }} </div>
      <div class="body"> {{ errorStore.body }} </div>
      <div class="buttons">
        <a @click="$router.back()" text="Go back"></a>
        |
        <a @click="$router.push('/')" text="Front page"></a>
      </div>
    </div>
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
  min-width: 100%;
  min-height: 100vh;
}

.error-message {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 32px;
  color: var(--c-text0);
  font-size: 20px;
  font-family: "barlow-medium";



  .title {
    color: var(--c-text-red);
    font-size: 32px;
    font-family: os-bold;
  }

  .body {
    white-space: pre;
  }

  .buttons {
    align-self: flex-end;
    display: flex;
    gap: 16px;
    color: var(--c-sf2);
    a:hover {
      color: var(--c-text0);
    }
  }

}



</style>