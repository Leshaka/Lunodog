<template>
  <td>
    <input v-once @input="$emit('update:value', this.rowId, this.Name, $event.target.innerText)" :value="Value"/>
  </td>
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

<style lang="scss" scoped>
input {
  background-color: inherit;
  border: none;
  color: var(--c-text1);
  outline: none;
  border: 1px red solid;
  height: 32px;
}
</style>