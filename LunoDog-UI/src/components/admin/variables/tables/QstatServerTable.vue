<template>
  <TableBase :Display="Display" :editMode="editMode" :isEdited="isEdited" :columnNames="columnNames" @addRow="addRow" @setMode="setMode" @commitRows="commitRows">
    <template v-if="editMode=='table'" #rows>
      <tr v-for="(row, index) in pendingRows">
        <CellText :updateKey="updateKey" :Value="row.host" :rowId="index" Name="host" @update:value="setValue"/>
        <CellNumber :updateKey="updateKey" :Value="row.port" :rowId="index" Name="port" @update:value="setValue"/>
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
import CellNumber from '@/components/admin/variables/tables/common/CellNumber.vue';

export default {
  mixins: [tableMixin],
  components: { TableBase, CellText, CellNumber},
  emits: ['update:value'],
  props: {
    guild: {type: Object, requeired: true},
    initialRows: {type: Array, requeired: true}
  },
  data() {
    return {
      Name: 'qstat_servers',
      Display: 'Server list',
      columnNames: ['Host', 'Port', 'Comment'],
      blankRow: {'host': '', 'port': 27960, 'comment': ''},
    }
  }
}
</script>