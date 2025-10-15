<template>
  <td>
    <VueSelect :modelValue="selOption" label="name" :placeholder="Placeholder" :options="Options" @update:modelValue="emitValue"/>
  </td>
</template>

<script>
  import VueSelect from "vue-select";

  export default {
    emits: ['update:value'],
    props: {
      Value: {type: String, requeired: false},
      rowId: {type: Number, requeired: true},
      Name: {type: String, requeired: true},
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
        this.$emit('update:value', this.rowId, this.Name, option ? option.id : null)
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

<style lang="scss" scoped>
.main {
  display: flex;
  flex-direction: column;
}

span.input:focus {
  outline: none;
}

span.options {
  position: relative;
}

ul {
	position: absolute;
	top: 0;
	left: 0;
	cursor: default;
  list-style: none;
}

li {
  background-color: var(--c-input);
  color: var(--c-text0);
  padding: 3px;
  border: 1px solid var(--c-sf0);;
}
</style>