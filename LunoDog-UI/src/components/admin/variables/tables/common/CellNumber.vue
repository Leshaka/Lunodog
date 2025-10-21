<template>
  <td class="editable" contenteditable="true" @input="$emit('update:value', this.rowId, this.Name, Number($event.target.innerText))">{{ value}}</td>
</template>

<script>
export default {
  emits: ['update:value'],
  props: {
      Value: {type: Number, requeired: true},
      rowId: {type: Number, requeired: true},
      Name: {type: String, requeired: true},
      updateKey: {type: Number, requeired: true}
  },
  data() {
    return {
      value: null
    }
  },
  mounted() {
    this.value = this.Value === null ? '' : this.Value;
  },
  watch: {
    updateKey() {
      this.value = this.Value === null ? '' : this.Value;
    }
  }
};
</script>