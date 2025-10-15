<template>
  <DiscordObjVar Name="admin_role" Display="Admin role" Placeholder="select a role" :Options="guild.roles" Description="Users with this role can edit the bot settings." :Value="cfg.admin_role" @update:value="updateConfig"/>
  <InfoLibraryTable :guild="guild" :initialRows="cfg.info_library" @update:value="updateConfig"/>
</template>

<script>
import DiscordObjVar from '@/components/admin/variables/DiscordObjVar.vue';
import InfoLibraryTable from '@/components/admin/variables/tables/InfoLibraryTable.vue'

import { cfg } from "@/config";


export default {
  components: { DiscordObjVar, InfoLibraryTable },

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