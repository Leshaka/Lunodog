<template>
  <BoolVar Name="qstat_enable" Display="Enable /qstat command" :Value="cfg.qstat_enable" @update:value="updateConfig"/>
  <StringVar Name="qstat_string" Display="Custom qstat server string" :Description="qstatStringDescription" :Value="cfg.qstat_string" :Default="qstatStringDefault" @update:value="updateConfig" Nullable/>
  <BoolVar Name="qstat_show_empty" Display="Show empty servers" :Value="cfg.qstat_show_empty" @update:value="updateConfig"/>
  <BoolVar Name="qstat_show_full" Display="Show full servers" :Value="cfg.qstat_show_full" @update:value="updateConfig"/>
  <OptionVar Name="qstat_sortby" Display="Sort by" :Options="sortbyOptions" :Value="cfg.qstat_sortby" @update:value="updateConfig" Default="host"/>
  <TextVar Name="qstat_filter" Display="Json filter" :Description="qstatFilterDescription" :Value="cfg.qstat_filter" :Default="qstatFilterDefault" @update:value="updateConfig" Nullable/>
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
    qstatStringDescription: 'Server display format string.' +
    '\n\nCommon server tags:' +
    '\n  {sv_maxclients} - number of slots' +
    '\n  {napname} - map' +
    '\n\nSpecial server tags (provided by the bot):' +
    '\n  {flag_icon} - server country flag emoji, custom flag icons can be set in the server list' +
    '\n  {private_icon} - conditional lock emoji if the server is private, empty space if not' +
    '\n  {name} - formatted server name' +
    '\n  {host} - address:port to connect to, this will use hostnames from the server list below' +
    '\n  {numclients} - number of connected players, minus bots if possible' +
    '\n  {p_string} - formatted list of connected players' +
    '\n\nYou can check your game/mod specific server tags at https://dpmaster.deathmask.net',
    qstatStringDefault: '{flag_icon} [**{gamename}**] {mapname}`/connect {host}`{private_icon}| `{name}`: `{p_string}`',
    sortbyOptions: ['numclients', 'host'],
    qstatFilterDefault: '{"gamename": "cpma"}',
    qstatFilterDescription: 'Json string in format {server_tag: value} to filter results with, value can be null to ensure the server tag is not present.' +
    '\nUseful to narrow results to a certain mod or version.'
  }},

  emits: ['updateConfig'],

  methods: {
    updateConfig(variable, value) {
      this.$emit('updateConfig', variable, value)
    }
  }
}
</script>
