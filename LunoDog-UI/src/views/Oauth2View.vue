<template>
  <div id="oauth-container">
    <div class="bh-loader big"></div>
  </div>
</template>

<script>
import apiMixin from '@/mixins/apiMixin.js'
import { useErrorStore } from '@/stores/error'

export default {
  mixins: [
    apiMixin
  ],

  data() {
    return {
      errorStore: useErrorStore()
    }
  },

  methods: {
    async auth(code) {
      const resp = await this.apiPost('/oauth', {'code': code});
      if (resp) {
        this.$router.push({name: 'admin-servers'});
      }
    }
  },

  mounted() {
    if (!this.$route.query.code) {
      this.errorStore.$patch({'title': 'Auth Error', 'body': 'Missing Oauth2 code.'});
      this.$router.push({name: 'error'});
      return;
    }
    this.auth(this.$route.query.code);
  }
}
</script>

<style>
#oauth-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>