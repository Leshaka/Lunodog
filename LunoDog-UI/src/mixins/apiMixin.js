import axios from 'axios'

import { useErrorStore } from '@/stores/error'
import { useUserStore } from '@/stores/user'

export default {
  inject: ["$apiURL"],

  setup() {
    const errorStore = useErrorStore();
    const userStore = useUserStore();
    return { userStore, errorStore }
  },

  methods: {

    async apiGet(path, query_data) {
      try {
        if (query_data) {
          path = path+'?'+new URLSearchParams(query_data).toString()
        }
        const response = await axios.get(this.$apiURL+path, {withCredentials: true});
        return response.data;
      } catch (e) {
        this.$_handleApiError(e);
      }
    },

    async apiPost(path, data) {
      try {
        const response = await axios.post(this.$apiURL+path, data, {withCredentials: true});
        return response.data;
      } catch (e) {
        this.$_handleApiError(e);
      }
    },

    async apiLogout() {
      try {
        // This request should logout us on the API server. Response tells browser delete our api_token cookie. Throws exc if status != 200
        await axios.get(this.$apiURL+'/logout', {withCredentials: true});
        this.userStore.$reset();  // delete our local user data
        this.$router.push({name: 'landing'});
      } catch (e) {
        this.$_handleApiError(e);
      }
    },

    $_handleApiError(e) {
      let errorData = {title: 'Unknown Error', body: ''}
      const errorStore = useErrorStore();

      // flush user data and redirect to login page (landing) on not authed response
      if (e.response?.status == 401) {
        this.userStore.$reset();
        this.$router.push({name: 'landing'})
        return;
      }

      // recieved an error response directly from the api server
      if (e.response?.data?.error) {
        errorData.title = e.response.data.error.status;
        errorData.body = e.response.data.error.message;
      }

      // received error from axios lib (such as unable to connect to host, etc)
      else if (e.name === 'AxiosError') {  
        errorData.title = 'API Error';
        errorData.body = e.message;
      }

      errorStore.$patch(errorData)
      this.$router.push({name: 'error'})
      throw new Error('An API error occured.');
    },

    async getOrFetchUser() {
      if (! this.userStore.user_id ) {
        let userData = await this.apiGet('/me')
        this.userStore.$patch(userData);
      }
    }

  },
}