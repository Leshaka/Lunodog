<template>
<div id="header-container">
<div id="header">
  <!--<img id="header-logo" src="/img/misc/logo_small.png"/>-->
  <RouterLink :to="{'name': 'landing'}"><span id="header-title">LunoDog</span></RouterLink>
  <div id="header-nav">
    <RouterLink :to="{'name': 'admin-servers'}">My servers</RouterLink>
    <a @click="apiLogout">Logout</a>
  </div>
  <div id="header-whitespace"></div>
  <div id="header-account">
    <span id="header-username">@{{userStore.username}}</span>
    <img v-if=userStore.avatar id="header-avatar" :src="`https://cdn.discordapp.com/avatars/${userStore.user_id}/${userStore.avatar}.webp?size=32`"/>
  </div>
</div>
<div id=header-subcolor></div>
</div>

<!--
<div v-if="path.length" id="subheader">
  <img v-if="icon" :src="icon"/>
  <template v-for="(item, index) in path">
    <RouterLink v-if="item.to" :to="item.to">{{ item.name }}</RouterLink>
    <span v-else>{{ item.name }}</span>
    <span v-if="index+1 != path.length">&nbsp»&nbsp</span>
  </template>
</div>
-->
</template>

<script>
import apiMixin from '@/mixins/apiMixin.js';
import { useUserStore } from '@/stores/user'

export default {
  mixins: [apiMixin],

  props: {
    path: {type: Array, required: false, default: []},
    icon: {type: String, required: false}
  },

  data() {
    return {
      userStore: useUserStore(),
      avatarUrl: 'https://cdn.discordapp.com/avatars/{target.id}/{target.avatar}.webp?size=32'
    }
  },

  mounted() {
    this.getOrFetchUser();
  },
}
</script>

<style lang="scss" scoped>

#header {
  height: 64px;
  width: 100%;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  font-family: os-regular;
  background-color: var(--c-sf1);
}

#header-subcolor {
  height: 24px;
  margin-top: -24px;
  background-color: var(--c-sf1);
  border-bottom: 3px solid var(--c-input);
}

#header-logo {
  width: 64px;
  height: 64px;
  margin-left: 16px;
}

#header-title {
  font-family: inter-extrabold;
  letter-spacing: 1px;
  font-size: 38px;
  color: var(--c-text2);
  margin-top: -2px;
  margin-left: 12px;
}

#header-nav {
  margin-left: 0px;
  a {
    color: var(--c-text0);
    font-size: 18px;
    margin-left: 24px;
    transition: 0.5s;
  }

  a:hover {
    color: var(--c-text2);
  }
}

#header-whitespace {
  flex: 1 1 auto;
}

#header-account {
  display: flex;
  align-items: center;
  margin-right: 12px;
  padding: 6px;
}

#header-username {
  color: var(--c-text1);
  font-size: 14px;
}

#header-avatar {
  width: 32px;
  margin-left: 12px;
}

#subheader {
  box-sizing: border-box;
  width: 100%;
  height: 37px;
  font-size: 14px;
  font-family: os-regular;
  color: var(--c-text1);
  background-color: var(--c-sf1);
  border-bottom: 1px solid var(--c-sf2);
  display: flex;
  align-items: center;
  padding-left: 12px;

  img {
    height: 24px;
    margin-right: 6px;
  }

  a:hover {
    color: var(--c-text3);
  }
}
</style>