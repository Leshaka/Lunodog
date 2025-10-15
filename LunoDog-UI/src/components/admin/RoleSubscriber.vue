<template>
  <BoolVar Name="rs_enable" Display="Enable role subscriber" :Value="cfg.rs_enable" @update:value="updateConfig"/>
  <RSEmojiTable :guild="guild" :initialRows="cfg.rs_emojis" @update:value="updateConfig"/>
  <RSCommandsTable :guild="guild" :initialRows="cfg.rs_commands" @update:value="updateConfig"/>
</template>

<script>
import BoolVar from '@/components/admin/variables/BoolVar.vue';
import RSEmojiTable from '@/components/admin/variables/tables/RSEmojiTable.vue'
import RSCommandsTable from '@/components/admin/variables/tables/RSCommandsTable.vue'


import { cfg } from "@/config";


export default {
  components: { BoolVar, RSEmojiTable, RSCommandsTable },

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