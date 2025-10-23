<template>
  <TableBase :Display="Display" :Description="Description" :editMode="editMode" :isEdited="isEdited" :columnNames="columnNames" @addRow="addRow" @setMode="setMode" @commitRows="commitRows">
    <template v-if="editMode=='table'" #rows>
      <tr v-for="(row, index) in pendingRows">
        <CellText :updateKey="updateKey" :Value="row.host" :rowId="index" Name="host" @update:value="setValue"/>
        <CellNumber :updateKey="updateKey" :Value="row.port" :rowId="index" Name="port" @update:value="setValue"/>
        <CellText :updateKey="updateKey" :Value="row.game_protocol" :rowId="index" Name="game_protocol" @update:value="setValue"/>
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
  components: { TableBase, CellText, CellNumber },
  emits: ['update:value'],
  props: {
    guild: {type: Object, requeired: true},
    initialRows: {type: Array, requeired: true}
  },
  data() {
    return {
      Name: 'qstat_master_servers',
      Display: 'Master server list',
      Description: 'List of master servers to query.' +
      '\nGame protocol is your game protocol string sent to the master server. Some game protocols:' +
      '\n68 - Quake III Arena' +
      '\nWarfork 26 - Warfork' +
      '\nXonotic 3 - Xonotic\n...',
      columnNames: ['Host', 'Port', 'Game protocol', 'Comment'],
      blankRow: {'host': '', 'port': 27950, 'game_protocol': '68', 'comment': ''}
    }
  }
}
</script>