<template>
  <BHHeader :path="[{'name': 'Admin'}, {'name': 'Servers'}]"/>
  <div id="page-container">
    <div id="title"><span>Select a server</span></div>
    <div v-if="isLoaded" id="server-list">
      <div v-for="g in guilds" class="server-entry">
        <div class="icon-container">
          <img :src="`https://cdn.discordapp.com/icons/${g.id}/${g.icon}.png?size=128`"/>
        </div>
        <div class="bottom">
          <div class="left">
            <span class="name">{{g.name}}</span>
            <span class="perms">{{ g.is_admin ? "Administrator" : "Member" }}</span>
          </div>
          <RouterLink :to="{name: 'admin-server', params: {guild_id: g.id}}"><BHButton class="go" :disabled="!g.is_admin" text="Go"/></RouterLink>
        </div>
      </div>
    </div>
    <div v-else class="bh-loader big"></div>

    <a :href="$inviteURL" target="_blank"><BHButton class="new-server" iconLeft="/img/misc/discord-mark-white.png" text="Add new server" large/></a>
  </div>
</template>

<script>
import apiMixin from '@/mixins/apiMixin.js';
import BHHeader from '@/components/BHHeader.vue';
import BHButton from '@/components/ui/BHButton.vue';


export default {
  inject: ["$inviteURL"],

  mixins: [apiMixin],

  components: { BHHeader, BHButton },

  data() {
    return {
      guilds: [],
      isLoaded: false
    }
  },

  mounted() {
    this.fetchGuilds();
  },

  methods: {
    async fetchGuilds() {
      this.guilds = await this.apiGet('/me/guilds');
      this.isLoaded = true;
    }
  }
}
</script>

<style lang="scss" scoped>
#page-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

#title {
  font-family: inter-extrabold;
  letter-spacing: 1px;
  font-size: 38px;
  color: var(--c-text2);
  padding: 32px 0 32px 0;
  text-align: center;
}

#server-list {
  width: 784px;
  box-sizing: border-box;
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  row-gap: 48px;
}

.server-entry {
  display: flex;
  flex-direction: column;

  .icon-container {
    background-color: var(--c-sf1);
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 240px;
    height: 140px;
    border-radius: 5px;

    img {
      width: 86px;
      height: 86px;
    }
  }

  .bottom {
    display: flex;
    gap: 16px;
    flex-wrap: nowrap;
    padding-top: 8px;
    font-family: os-regular;
    align-items: center;
  }

  .left {
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
  }

  button.go {
    //background-color: var(--c-text-green);
    min-width: 48px;
  }

  .name {
    color: var(--c-text1);
  }

  .perms {
    color: var(--c-text0);
  }
}

.new-server {
  margin-top: 48px;
  background-color: #5865F2;
  color: white;
  margin-bottom: 48px;
}

.new-server:hover {
  background-color: #6773f0;
}
</style>