<template>
  <DiscordObjVar Name="isolator_role" Display="Isolator role" Placeholder="select a role" :Options="guild.roles" Description="Role for the isolated users." :Value="cfg.isolator_role" @update:value="updateConfig"/>
  <DiscordObjVar Name="isolator_mute_role" Display="Mute role" Placeholder="select a role" :Options="guild.roles" Description="Role for the muted users." :Value="cfg.isolator_mute_role" @update:value="updateConfig"/>
  <DiscordObjVar Name="isolator_log_channel" Display="Audit channel" Placeholder="select a channel" Description="Log all isolator changes in this channel." :Options="guild.text_channels" :Value="cfg.isolator_log_channel" @update:value="updateConfig"/>
</template>

<script>
import DiscordObjVar from '@/components/admin/variables/DiscordObjVar.vue';

import { cfg } from "@/config";


export default {
  components: { DiscordObjVar },

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