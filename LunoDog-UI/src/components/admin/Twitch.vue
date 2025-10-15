<template>
  <BoolVar Name="twitch_enable" Display="Enable Twitch announcements" :Value="cfg.twitch_enable" @update:value="updateConfig"/>
  <DiscordObjVar Name="twitch_announcement_channel" Display="Announcement channel" Placeholder="select a channel" :Options="guild.text_channels" Description="Channel for stream announcements." :Value="cfg.twitch_announcement_channel" @update:value="updateConfig"/>
  <BoolVar Name="twitch_summary" Display="Post summary" Description="Announce stream summary info when a stream has ended." :Value="cfg.twitch_summary" @update:value="updateConfig"/>
  <TwitchChannelsTable  :guild="guild" :initialRows="cfg.twitch_channels" @update:value="updateConfig"/>
</template>

<script>
import BoolVar from '@/components/admin/variables/BoolVar.vue';
import StringVar from '@/components/admin/variables/StringVar.vue';
import TextVar from '@/components/admin/variables/TextVar.vue';
import DiscordObjVar from '@/components/admin/variables/DiscordObjVar.vue';
import TwitchChannelsTable from '@/components/admin/variables/tables/TwitchChannelsTable.vue';


import { cfg } from "@/config";


export default {
  components: { BoolVar, StringVar, TextVar, DiscordObjVar, TwitchChannelsTable },

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