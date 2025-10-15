<template>
  <TableBase :Display="Display" :Description="Description" :editMode="editMode" :isEdited="isEdited" :columnNames="columnNames" @addRow="addRow" @setMode="setMode" @commitRows="commitRows">
    <template v-if="editMode=='table'" #rows>
      <tr v-for="(row, index) in pendingRows">
        <CellText :updateKey="updateKey" :Value="row.message_id" :rowId="index" Name="message_id" @update:value="setValue"/>
        <CellText :updateKey="updateKey" :Value="row.emoji" :rowId="index" Name="emoji" @update:value="setValue"/>
        <CellDiscordObj :Value="row.role" Placeholder="Select a role" :Options="guild.roles" :rowId="index" Name="role" @update:value="setValue"/>
        <CellText :updateKey="updateKey" :Value="row.comment" :rowId="index" Name="comment" @update:value="setValue"/>
        <td class="delete"><img src="/img/admin/delete.png" @click="deleteRow(index)"/></td>
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
import CellDiscordObj from '@/components/admin/variables/tables/common/CellDiscordObj.vue';

export default {
  mixins: [tableMixin],
  components: { TableBase, CellText, CellDiscordObj },
  emits: ['update:value'],
  props: {
    guild: {type: Object, requeired: true},
    initialRows: {type: Array, requeired: true}
  },
  data() {
    return {
      Name: 'rs_emojis',
      Display: 'Emoji triggers',
      Description: 'Emoji reaction to role mappings. React to message with emoji to obtain role(s), remove reaction to remove.\nA message ID can be copied by turning on developer mode in Discord.\nEmoji can be a UTF-8 emoji or a custom emoji name.',
      columnNames: ['Message ID', 'Emoji', 'Role', 'Comment'],
      blankRow: {'message_id': '', 'emoji': '', 'role': null, 'comment': ''}
    }
  }
}
</script>