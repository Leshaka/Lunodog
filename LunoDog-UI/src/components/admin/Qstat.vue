<template>
  <BoolVar Name="qstat_enable" Display="Enable /qstat command" :Value="cfg.qstat_enable" @update:value="updateConfig"/>
  <StringVar Name="qstat_string" Display="Custom qstat server string" :Description="qstatStringDescription" :Value="cfg.qstat_string" :Default="qstatStringDefault" @update:value="updateConfig" Nullable/>
  <BoolVar Name="qstat_show_empty" Display="Show empty servers" :Value="cfg.qstat_show_empty" @update:value="updateConfig"/>
  <BoolVar Name="qstat_show_full" Display="Show full servers" :Value="cfg.qstat_show_full" @update:value="updateConfig"/>
  <OptionVar Name="qstat_sortby" Display="Sort by" :Options="sortbyOptions" :Value="cfg.qstat_sortby" @update:value="updateConfig" Default="host"/>
  <TextVar Name="qstat_filter" Display="Json filter" :Value="cfg.qstat_filter" :Default="qstatFilterDefault" @update:value="updateConfig" Nullable/>
  <QstatMasterServerTable :guild="guild" :initialRows="cfg.qstat_master_servers" @update:value="updateConfig"/>
  <QstatServerTable :guild="guild" :initialRows="cfg.qstat_servers" @update:value="updateConfig"/>
</template>

<script>
import BoolVar from '@/components/admin/variables/BoolVar.vue';
import StringVar from '@/components/admin/variables/StringVar.vue';
import TextVar from '@/components/admin/variables/TextVar.vue';
import OptionVar from '@/components/admin/variables/OptionVar.vue';
import QstatMasterServerTable from '@/components/admin/variables/tables/QstatMasterServerTable.vue'
import QstatServerTable from '@/components/admin/variables/tables/QstatServerTable.vue'

export default {
  components: { BoolVar, StringVar, TextVar, OptionVar, QstatMasterServerTable, QstatServerTable },

  props: {
    cfg: {type: Object, requeired: true},
    guild: {type: Object, requeired: true}
  },

  data() {return {
    qstatStringDescription: 'Server display format string. Available tags:' +
    '\n{flag_icon} - server location icon' +
    '\n{numclients} - number of connected players' +
    '\n{sv_maxclients} - number of slots' +
    '\n{mode_current} - game mode' +
    '\n{napname} - map' +
    '\n{host} - address and port to connect to' +
    '\n{name} - server name' +
    '\n{gameversion} - version of the mod' +
    '\n{p_string} - list of connected players',
    qstatStringDefault: '> {flag_icon} [**{numclients}**/{sv_maxclients}] [**{mode_current}**] {mapname} `/connect {host}` | `{name}`@***{gameversion}*** : {p_string}',
    sortbyOptions: ['host', 'numclients'],
    qstatFilterDefault: '{"gamename": "cpma"}'
  }},

  emits: ['updateConfig'],

  methods: {
    updateConfig(variable, value) {
      this.$emit('updateConfig', variable, value)
    }
  }
}
</script>
