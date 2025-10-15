<template>
  <div class="bh-variable">
    <div class="header">
      <div class="left">
        <div class="title">{{ Display }}</div>
        <div v-if="Description" class="description">{{ Description }}</div>
      </div>
      <div class="middle"></div>
      <div class="right">
        <a v-if="Default" class="default" @click="$emit('update:value', Name, Default)">
          <img src="/img/icons/admin/reset.png"/>
          <div class="bh-tooltip">Reset to default</div>
        </a>
        <label class="bh-switch" v-if="Nullable">
          <input :checked="Value" type="checkbox" @input="$emit('update:value', Name, $event.target.checked ? '' : null)"/><span></span>
        </label>
      </div>
    </div>
    <div class="content" v-if="Value != null">
      <textarea rows=5 class="bh-input" :value="Value" :placeholder="Placeholder" @input="$emit('update:value', Name, $event.target.value)"></textarea>
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
    Placeholder: {type: String, requeired: false},
    Value: {type: String, requeired: false},
    Nullable: {type: Boolean, default: false},
    Default: {type: String, requeired: false}
  }
}
</script>

<style lang="scss" scoped>
.bh-input {
  width: 100%;
}
</style>