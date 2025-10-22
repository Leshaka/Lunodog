<template>  
  <div id="about-container">
    <div id="about-header">
      <a href="https://github.com/Leshaka/lunodog" target="_blank">GitHub</a>
      <a href="https://discord.gg/nUEscwptgP" target="_blank">#promode.ru</a>
    </div>
    <div id="about-center">
      <span class="title">LunoDog</span>
      <span class="description">LunoDog is a multi-purpose discord bot with modular design made for #promode.ru community.</span>
      <template v-if="isLoaded">
        <RouterLink v-if="userStore.user_id" :to="{'name': 'admin-servers'}"><BHButton text="Enter"/></RouterLink>
        <a v-else :href="$oauthURL"><BHButton class="dc" iconLeft="/img/misc/discord-mark-white.png" text="Login with discord" large/></a>
      </template>
      <div v-else class="bh-loader"></div>

    </div>
  </div>
</template>
  
<script>
  import apiMixin from '@/mixins/apiMixin.js';
  import { useUserStore } from '@/stores/user'
  import BHButton from '@/components/ui/BHButton.vue';
  
  
  export default {
    inject: ["$oauthURL"],
  
    mixins: [apiMixin],

    components: { BHButton },

    data() {
      return {
        userStore: useUserStore(),
        isLoaded: false
      }
    },

    async mounted() {
      await this.getOrFetchUser();
      this.isLoaded = true;
  },
  }
</script>
  
<style lang="scss" scoped>

  #about-container {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    height: 100vh;
  }

  #about-header {
    display: flex;
    flex-direction: row;
    gap: 12px;
    justify-content: center;
    margin: 12px;

    a {
      font-family: os-regular;
      font-size: 16px;
      color: var(--c-text0);
    }

    a:hover {
      color: var(--c-text2);
    }
  }

  #about-center {
    display: flex;
    flex-direction: column;
    justify-content: center;
    flex: 1 2 auto;
    gap: 16px;
    align-items: center;

    span.title {
      font-family: inter-extrabold;
      letter-spacing: 1px;
      font-size: 38px;
      color: var(--c-text2);
    }

    span.description {
      font-family: os-regular;
      font-size: 16px;
      color: var(--c-text0);
    }

    button.dc {
      background-color: #5865F2;
      color: white;
      margin-top: 32px;
    }

    button.dc:hover {
      background-color: #6773f0;
    }
  }


</style>