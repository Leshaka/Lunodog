<template>
  <BoolVar Name="yt_enable" Display="Enable YouTube announcements" :Value="cfg.twitch_enable" @update:value="updateConfig"/>
  <DiscordObjVar Name="yt_announcement_channel" Display="Announcement channel" Placeholder="select a channel" :Options="guild.text_channels" Description="Channel for stream announcements." :Value="cfg.yt_announcement_channel" @update:value="updateConfig"/>
  <YTChannelsTable  :guild="guild" :initialRows="cfg.yt_channels" @update:value="updateConfig"/>
</template>

<script>
import BoolVar from '@/components/admin/variables/BoolVar.vue';
import StringVar from '@/components/admin/variables/StringVar.vue';
import TextVar from '@/components/admin/variables/TextVar.vue';
import DiscordObjVar from '@/components/admin/variables/DiscordObjVar.vue';
import YTChannelsTable from '@/components/admin/variables/tables/YTChannelsTable.vue';


import { cfg } from "@/config";


export default {
  components: { BoolVar, StringVar, TextVar, DiscordObjVar, YTChannelsTable },

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