<template>
  <TableBase :Display="Display" :Description="Description" :editMode="editMode" :isEdited="isEdited" :columnNames="columnNames" @addRow="addRow" @setMode="setMode" @commitRows="commitRows">
    <template v-if="editMode=='table'" #rows>
      <tr v-for="(row, index) in pendingRows">
        <CellText :updateKey="updateKey" :Value="row.channel" :rowId="index" Name="channel" @update:value="setValue"/>
        <CellBool :Value="row.post_videos" :rowId="index" Name="videos" @update:value="setValue"/>
        <CellBool :Value="row.post_shorts" :rowId="index" Name="videos" @update:value="setValue"/>
        <CellBool :Value="row.post_broadcasts" :rowId="index" Name="broadcasts" @update:value="setValue"/>
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
      Name: 'yt_channels',
      Display: 'Youtube channels',
      Description: 'List of YouTube channels to keep track of.' +
      '\nChannel is the channel name from the youtube channel URL (https://www.youtube.com/@Leshkawsw = Leshkawsw).',
      columnNames: ['Channel', 'Announce videos', 'Shorts', 'Broadcasts'],
      blankRow: {'channel': '', 'post_videos': true, 'post_shorts': true, 'post_broadcasts': true},
      defaultRows: []
    }
  }
}
</script>