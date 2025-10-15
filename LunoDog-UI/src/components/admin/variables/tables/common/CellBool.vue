<template>
  <td class="checkbox"><input type="checkbox" @input="$emit('update:value', this.rowId, this.Name, $event.target.checked)" :checked="Value"/></td>
</template>

<script>
export default {
  emits: ['update:value'],
  props: {
      Value: {type: String, requeired: true},
      rowId: {type: Number, requeired: true},
      Name: {type: String, requeired: true}
  }
};
</script>