<template>
  <TableBase :Display="Display" :Description="Description" :editMode="editMode" :isEdited="isEdited" :columnNames="columnNames" @addRow="addRow" @setMode="setMode" @commitRows="commitRows">
    <template v-if="editMode=='table'" #rows>
      <tr v-for="(row, index) in pendingRows">
        <CellText :updateKey="updateKey" :Value="row.name" :rowId="index" Name="name" @update:value="setValue"/>
        <CellDiscordObj :Value="row.role" Placeholder="Select a role" :Options="guild.roles" :rowId="index" Name="role" @update:value="setValue"/>
        <CellBool :Value="row.allow_sub" :rowId="index" Name="allow_sub" @update:value="setValue"/>
        <CellBool :Value="row.allow_unsub" :rowId="index" Name="allow_unsub" @update:value="setValue"/>
        <CellText :updateKey="updateKey" :Value="row.comment" :rowId="index" Name="comment" @update:value="setValue"/>
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
import CellDiscordObj from '@/components/admin/variables/tables/common/CellDiscordObj.vue';

export default {
  mixins: [tableMixin],
  components: { TableBase, CellText, CellBool, CellDiscordObj },
  emits: ['update:value'],
  props: {
    guild: {type: Object, requeired: true},
    initialRows: {type: Array, requeired: true}
  },
  data() {
    return {
      Name: 'rs_commands',
      Display: 'Slash command subscriptions',
      Description: 'Roles users can subscribe to with /role subscribe and /role unsubscribe commands.\nSubscription name will appear in the slash command autocompletion menu.\nOne subsciption name can be stacked with multiple roles.',
      columnNames: ['Subscription name', 'Role', 'Allow subscribe', 'Allow unsubscribe', 'Comment'],
      blankRow: {'name': '', 'role': null, 'allow_sub': true, 'allow_unsub': true, 'comment': ''}
    }
  }
}
</script>