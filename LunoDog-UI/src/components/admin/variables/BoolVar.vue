<template>
<div class="variable">
  <div class="header">
    <div class="left">
      <div class="title">{{ Display }}</div>
      <div class="description">{{ Description }}</div>
    </div>
    <div class="middle"></div>
    <div class="right">
      <label class="bh-switch"><input :checked="Value" type="checkbox" @input="$emit('update:value', Name, $event.target.checked)"/><span></span></label>
    </div>
  </div>
</div>
</template>

<script>
export default {
  emits: ['update:value'],
  props: {
    Name: {type: String, requeired: true},
    Display: {type: String},
    Description: {type: String, requeired: false},
    Value: {type: Boolean, requeired: false}
  }
}
</script>