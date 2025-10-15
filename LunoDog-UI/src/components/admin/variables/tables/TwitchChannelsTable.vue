<template>
  <TableBase :Display="Display" :Description="Description" :editMode="editMode" :isEdited="isEdited" :columnNames="columnNames" @addRow="addRow" @setMode="setMode" @commitRows="commitRows">
    <template v-if="editMode=='table'" #rows>
      <tr v-for="(row, index) in pendingRows">
        <CellText :updateKey="updateKey" :Value="row.channel" :rowId="index" Name="channel" @update:value="setValue"/>
        <CellText :updateKey="updateKey" :Value="row.allowed_games" :rowId="index" Name="allowed_games" @update:value="setValue"/>
        <CellText :updateKey="updateKey" :Value="row.message_text" :rowId="index" Name="message_text" @update:value="setValue"/>
        <td class="delete"><img src="/img/icons/admin/delete.png" @click="deleteRow(index)"/></td>
      </tr>
      <tr v-if="pendingRows.length == 0"><td class="empty" :colspan="Object.keys(blankRow).length+1">table is empty</td></tr>
    </template>
    <template v-if="editMode=='json'" #json>
      <textarea :class="{ 'error': pendingJsonError }"rows=10 class="bh-input" :value="pendingJson" @input="setJson($event.target.value)"></textarea>
    </template>
  </TableBase>
</template>

<script>

import tableMixin from '@/components/admin/variables/tables/common/tableMixin.js';
import TableBase from '@/components/admin/variables/tables/common/TableBase.vue';
import CellText from '@/components/admin/variables/tables/common/CellText.vue';
import CellBool from '@/components/admin/variables/tables/common/CellBool.vue';

export default {
  mixins: [tableMixin],
  components: { TableBase, CellText, CellBool },
  emits: ['update:value'],
  props: {
    guild: {type: Object, requeired: true},
    initialRows: {type: Array, requeired: true}
  },
  data() {
    return {
      Name: 'twitch_channels',
      Display: 'Twitch channels',
      Description: 'List of twitch channels to keep track of.' +
      '\nChannel is the twitch channel name.' +
      '\nAllowed games is list of games as on twitch separated by a comma, asterisk means any game will be announced.' +
      '\nMessage is optional text to send with the stream announcement embed.',
      columnNames: ['Channel', 'Allowed games', 'Message'],
      blankRow: {'channel': '', 'allowed_games': '*', 'message_text': ''},
      defaultRows: []
    }
  }
}
</script>