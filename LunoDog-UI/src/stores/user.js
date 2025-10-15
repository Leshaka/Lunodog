import { defineStore } from 'pinia'

export const useUserStore = defineStore('user',  {
  state: () => {
    return {
      user_id: null,
      username: null,
      avatar: null
    }
  }
})