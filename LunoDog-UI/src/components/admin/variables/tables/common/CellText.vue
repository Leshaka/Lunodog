<template :key="Value">
  <td class="editable" contenteditable="true" spellcheck="false" @input="$emit('update:value', this.rowId, this.Name, $event.target.innerText.trimRight())">{{ value }}</td>
</template>

<script>
export default {
  emits: ['update:value'],
  props: {
      Value: {type: String, requeired: true},
      rowId: {type: Number, requeired: true},
      Name: {type: String, requeired: true},
      updateKey: {type: Number, requeired: false, default: 0}
  },
  data() {
    return {
      value: ''
    }
  },
  mounted() {
    this.value = this.Value;
  },
  watch: {
    updateKey() {
      this.value = this.Value;
    }
  }
};
</script>