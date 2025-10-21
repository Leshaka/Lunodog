<template>
<div id="page-container">
  <BHHeader/>
  <div v-if="!isLoaded" id="loader-container"><div class="bh-loader big"></div></div>
  <div v-else id="guild-container">
    <div id="sb-container">
      <div id="sb-header">
        <img :src="`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=128`"/>
        <div class="left">
          <span class="title">{{guild.name}}</span>
          <RouterLink :to="{'name': 'admin-servers'}" class="sub">other servers</RouterLink>
        </div>
      </div>
      <div id="sb-menu">
        <RouterLink :to="{name: 'admin-server', params: {section: 'Bot'}}" class="entry" :class="{selected : section=='Bot'}">
          <img src="/img/icons/admin/modules/bot.png"/>Bot
        </RouterLink>
        <RouterLink :to="{name: 'admin-server', params: {section: 'Greetings'}}" class="entry" :class="{selected : section=='Greetings'}">
          <img src="/img/icons/admin/modules/greetings.png"/>Greetings
        </RouterLink>
        <RouterLink :to="{name: 'admin-server', params: {section: 'Role subscriber'}}" class="entry" :class="{selected : section=='Role subscriber'}">
          <img src="/img/icons/admin/modules/role_subscriber.png"/>Role subscriber
        </RouterLink>
        <RouterLink :to="{name: 'admin-server', params: {section: 'Qstat'}}" class="entry" :class="{selected : section=='Qstat'}">
          <img src="/img/icons/admin/modules/qstat.png"/>Qstat
        </RouterLink>
        <RouterLink :to="{name: 'admin-server', params: {section: 'Isolator'}}" class="entry" :class="{selected : section=='Isolator'}">
          <img src="/img/icons/admin/modules/isolator.png"/>Isolator
        </RouterLink>
        <RouterLink :to="{name: 'admin-server', params: {section: 'Twitch'}}" class="entry" :class="{selected : section=='Twitch'}">
          <img src="/img/icons/admin/modules/twitch.png"/>Twitch
        </RouterLink>
        <RouterLink :to="{name: 'admin-server', params: {section: 'YouTube'}}" class="entry" :class="{selected : section=='YouTube'}">
          <img src="/img/icons/admin/modules/yt.png"/>YouTube
        </RouterLink>
      </div>
    </div>
    <div id="content-container">
      <div class="section-title">{{ section }} settings</div>
      <BotConf v-if="section=='Bot'" :guild="this.guild" :cfg="this.pendingConfig" @updateConfig="updateConfig"/>
      <GreetingsConf v-if="section=='Greetings'" :guild="this.guild" :cfg="this.pendingConfig" @updateConfig="updateConfig"/>
      <RoleSubscriberConf v-if="section=='Role subscriber'" :guild="this.guild" :cfg="this.pendingConfig" @updateConfig="updateConfig"/>
      <QstatConf v-if="section=='Qstat'" :guild="this.guild" :cfg="this.pendingConfig" @updateConfig="updateConfig"/>
      <IsolatorConf v-if="section=='Isolator'" :guild="this.guild" :cfg="this.pendingConfig" @updateConfig="updateConfig"/>
      <TwitchConf v-if="section=='Twitch'" :guild="this.guild" :cfg="this.pendingConfig" @updateConfig="updateConfig"/>
      <YouTubeConf v-if="section=='YouTube'" :guild="this.guild" :cfg="this.pendingConfig" @updateConfig="updateConfig"/>
      <div class="submit-container">
        <button class="revert" text="Revert" :disabled="!configChanged" @click="revertChanges">Revert</button>
        <button class="save" text="Apply" :disabled="!configChanged" @click="saveChanges">Apply</button>
    </div>
    </div>
  </div>
</div>
</template>

<script>
import "@/styles/bh-variable.scss";
import "@/styles/bh-input.scss";
import "@/styles/bh-select.scss";
import "@/styles/bh-switch.scss";
import "@/styles/bh-tooltip.scss";
import "@/styles/packages/vue-select.css"

import apiMixin from '@/mixins/apiMixin.js';
import BHHeader from '@/components/BHHeader.vue';
import BotConf from '@/components/admin/Bot.vue';
import GreetingsConf from '@/components/admin/Greetings.vue';
import RoleSubscriberConf from '@/components/admin/RoleSubscriber.vue';
import QstatConf from '@/components/admin/Qstat.vue';
import IsolatorConf from '@/components/admin/Isolator.vue';
import TwitchConf from '@/components/admin/Twitch.vue';
import YouTubeConf from '@/components/admin/YouTube.vue';

import { toRaw } from 'vue';


export default {
  mixins: [apiMixin],

  props: {
    guild_id: {type: String, requeired: true},
    section: {type: String, requeired: false, default: 'Bot'}
  },

  components: { BHHeader, BotConf, GreetingsConf, RoleSubscriberConf, QstatConf, IsolatorConf, TwitchConf, YouTubeConf },

  data() {
    return {
      guild: null,
      isLoaded: false,
      configChanged: false,
      pendingConfig: {}
    }
  },

  mounted() {
    this.fetchGuildConfig();
  },

  methods: {
    async fetchGuildConfig() {
      this.guild = await this.apiGet(`/config/get?guild_id=${this.guild_id}`);
      this.pendingConfig = structuredClone(toRaw(this.guild.config));
      this.configChanged = false;
      this.isLoaded = true;
    },
    updateConfig(variable, value) {
      console.log(`update config.... set ${variable} to ${value}`);
      this.pendingConfig[variable] = value;
      this.updateChanged();
    },
    updateChanged() {
      if (JSON.stringify(this.pendingConfig) === JSON.stringify(this.guild.config)) {
        this.configChanged = false;
      } else {
        this.configChanged = true;
      }
    },
    revertChanges() {
      this.pendingConfig = structuredClone(toRaw(this.guild.config));
      this.configChanged = false;
    },
    async saveChanges() {
      this.isLoaded = false;
      let resp = await this.apiPost('/config/update', {guild_id: this.guild.id, cfg: this.pendingConfig});
      await this.fetchGuildConfig();
    }
  }

}
</script>

<style lang="scss" scoped>
#page-container {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  height: 100vh;
  background-color: unset;
  min-width: max-content;
}

#loader-container {
  flex: 1 1 auto;
  align-self: stretch;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 16px;
}

#guild-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 16px;
}


.loader {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 16px;
}

#sb-container {
  width: 350px;
  background-color: var(--c-sf1);
  border-radius: 16px 16px 8px 8px;
  box-shadow: 3px 3px var(--c-input);
}

#sb-header {
  background-color: var(--c-sf2);
  border-radius: 16px;
  padding: 16px;
  display: flex;

  img {
    width: 64px;
    height: 64px;
  }

  .left {
    margin-left: 12px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .title {
    color: var(--c-text1);
    font-family: os-extrabold;
    font-size: 24px;
  }

  .sub {
    color: var(--c-text0);
    font-family: os-regular;
    text-decoration: underline;
  }
}

#sb-menu {
  display: flex;
  flex-direction: column;
  padding: 16px;

  .entry {
    color: var(--c-text0);
    font-family: os-medium;
    border-bottom: 1px solid var(--c-sf1);
    border-right: 1px solid var(--c-sf1);
    padding: 8px 8px 8px 16px;
    display: flex;
    align-items: center;
  }

  img {
    width: 24px;
    margin-right: 16px;
  }

  .entry.selected, .entry:hover {
    color: var(--c-text1);
    background-color: var(--c-sf2);
    border-bottom: 1px solid var(--c-sf0);
    border-right: 1px solid var(--c-sf0);
  }
}

#content-container {
  width: 1024px;
  margin-left: 16px;
  padding: 0 16px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: stretch;
}

.section-title {
  color: var(--c-text0);
  font-family: inter-extrabold;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--c-sf1);
  letter-spacing: 1px;
  font-size: 20px;
}

.submit-container {
  padding: 16px 16px 0 16px;
  display: flex;
  gap: 16px;
  justify-content: flex-end;

  button {
    all: unset;
    background-color: unset;
    font-family: os-medium;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px;
    color: var(--c-btn-text);
    border-radius: 6px;
    width: 64px;
    height: 32px;
    cursor: pointer;
    transition: all 0.3s;
    user-select: none;
  }

  button:disabled {
    cursor: not-allowed;
    filter: grayscale(60%) contrast(50%);
  }

  button:not([disabled]):hover {
    filter: brightness(115%);
  }

  button:focus {
    outline: 2px solid var(--c-text-blue);
  }
  button:focus:not(:focus-visible) {
    outline: none
  }

  button:not([disabled]):active {
    transform: scale(0.98);
  }

  .save {
    background-color: var(--c-text-green);
    box-shadow: 2px 2px rgba(0, 0, 0, 0.5);
  }

  .revert {
    color: var(--c-text0);
  }

  .revert:disabled {
    visibility: hidden;
  }

  .revert:not([disabled]):hover {
    background-color: var(--c-sf2);
    color: var(--c-text1);
  }
}
</style>
