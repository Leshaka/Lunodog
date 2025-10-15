<template>
  <div class="bh-variable">
    <div class="header">
      <div class="left">
        <div class="title">{{ Display }}</div>
        <div v-if="Description" class="description">{{ Description }}</div>
      </div>
    </div>
    <div class="content">
      <VueSelect :modelValue="selOption" label="name" :placeholder="Placeholder" :options="Options" @update:modelValue="emitValue"/>
    </div>
  </div>
  </template>
  
  <script>
  import VueSelect from "vue-select";

  export default {
    emits: ['update:value'],
    props: {
      Name: {type: String, requeired: true},
      Display: {type: String},
      Description: {type: String, requeired: false},
      Value: {type: String, requeired: false},
      Placeholder: {type: String, requeired: false},
      Options: {type: Array, requeired: true}
    },
    components: { VueSelect },
    data() {
      return {
        selOption: null
      }
    },
    methods: {
      emitValue(option) {
        this.$emit('update:value', this.Name, option ? option.id : null)
      },
      setOption() {
        this.selOption = this.Value ? this.Options.find((element) => element.id == this.Value) : null;
      },
    },
    mounted() {
      this.setOption();
    },
    watch: {
      Value(newValue, oldValue) {
        this.setOption();
      }
    },
  }
</script>