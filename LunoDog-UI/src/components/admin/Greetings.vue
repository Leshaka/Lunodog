<template>
  <BoolVar Name="greetings_enable" Display="Enable greetings" :Value="cfg.greetings_enable" @update:value="updateConfig"/>
  <DiscordObjVar Name="greetings_welcome_channel" Display="Welcome channel" Placeholder="select a channel" :Options="guild.text_channels" Description="Channel for welcome messages." :Value="cfg.greetings_welcome_channel" @update:value="updateConfig"/>
  <TextVar Name="greetings_welcome_message" Display="Welcome message" Description="Message to send on new member join. Use {member} for the member mention." :Value="cfg.greetings_welcome_message" @update:value="updateConfig" Nullable/>
  <TextVar Name="greetings_welcome_back_message" Display="Welcome back message" Description="Message to send on member re-join." :Value="cfg.greetings_welcome_back_message" @update:value="updateConfig" Nullable/>
  <DiscordObjVar Name="greetings_goodbye_channel" Display="Goodbye channel" Placeholder="select a channel" :Options="guild.text_channels" Description="Channel for goodbye messages." :Value="cfg.greetings_goodbye_channel" @update:value="updateConfig"/>
  <TextVar Name="greetings_goodbye_message" Display="Goodbye message" Description="Message to send on member leaving the server. Use {member} for the member mention." :Value="cfg.greetings_goodbye_message" @update:value="updateConfig" Nullable/>
  <TextVar Name="greetings_goodbye_again_message" Display="Goodbye again message" Description="Message to send on member leaving the server multiple times." :Value="cfg.greetings_goodbye_again_message" @update:value="updateConfig" Nullable/>
</template>

<script>
import BoolVar from '@/components/admin/variables/BoolVar.vue';
import StringVar from '@/components/admin/variables/StringVar.vue';
import TextVar from '@/components/admin/variables/TextVar.vue';
import DiscordObjVar from '@/components/admin/variables/DiscordObjVar.vue';

import { cfg } from "@/config";


export default {
  components: { BoolVar, StringVar, TextVar, DiscordObjVar },

  props: {
    cfg: {type: Object, requeired: true},
    guild: {type: Object, requeired: true}
  },

  emits: ['updateConfig'],

  methods: {
    updateConfig(variable, value) {
      this.$emit('updateConfig', variable, value)
    }
  }
}
</script>