<template>
  <div class="variable">
    <div class="header">
      <div class="left">
        <div class="title">{{ Display }}</div>
        <div v-if="Description" class="description">{{ Description }}</div>
      </div>
    </div>

    <div class="content" v-if="editMode=='table'">
      <table class="table-editable">
        <tbody>
          <tr><th v-for="colName in columnNames">{{ colName }}</th><th></th></tr>
          <slot name="rows"></slot>
          <tr><td :colspan="columnNames.length+1" class="add" @click="$emit('addRow')">+ add row</td></tr>
        </tbody>
      </table>
      <div class="btn-container">
        <BHButton text="Change" class="save" :disabled="!isEdited" @click="$emit('commitRows')"/>
        <BHButton text="Edit as json" @click="$emit('setMode', 'json')"/>
      </div>
    </div>

    <div class="content" v-if="editMode=='json'">
      <slot name="json"></slot>
      <div class="btn-container">
        <BHButton text="Change" @click="$emit('setMode', 'table')"/>
      </div>
    </div>

  </div>
</template>

<script>
import BHButton from '@/components/ui/BHButton.vue';

export default {
  emits: ['addRow', 'setMode', 'commitRows'],
  components: { BHButton },
  props: {
    Display: {type: String},
    Description: {type: String, requeired: false, default: null},
    columnNames: {type: Array, requeired: true},
    editMode: {type: String, default: 'table'},
    isEdited: {type: Boolean, requeired: true}
  }
}
</script>

<style lang="scss">
.variable {
  padding: 8px 16px 8px 16px;
  border-radius: 8px;
  background-color: var(--c-sf1);
  box-shadow: 3px 3px var(--c-input);
  color: var(--c-text1);
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
}

.title {
  font-family: os-medium;
  font-size: 18px;
}

.description {
  margin-top: 6px;
  font-family: barlow-regular;
  color: var(--c-text0);
  white-space: pre;
}

.content {
  border-top: 1px solid var(--c-sf1);
  margin-top: 8px;
  padding-top: 8px;
}

.bh-input {
  width: 100%;
}

.table-editable {
    min-width: 400px;
    text-align: left;
    background-color: var(--c-sf0);

    tr:nth-child(odd) {
      background-color: var(--c-sf0odd);
    }

    tr:hover {
      background: var(--c-sf1);
    }

    th {
      padding: 8px;
      font-family: barlow-medium;
      color: var(--c-text1);
      background-color: var(--c-sf2);
    }

    td.editable {
      padding: 8px;
      font-family: barlow-regular;
      white-space: pre-wrap;
    }

    td.checkbox {
      text-align: center;
    }

    td.empty {
      padding: 8px;
      font-family: barlow-regular;
      color: var(--c-text0);
      text-align: center;
      background-color: var(--c-sf0);
    }
  
    td {
      color: var(--c-text1);
    }

    td:focus {
      outline: none;
    }

    td.delete {
      padding: 8px;
      img {
        width: 20px;
        height: 20px;
        cursor: pointer;
      }
    }

    td.add {
      font-family: barlow-medium;
      color: var(--c-text-green);
      border-bottom: 1px solid var(--c-sf2);
      padding: 8px;
      text-align: center;
      cursor: pointer;
    }
}

textarea.error {
  border: 1px solid var(--c-text-red);
}

.btn-container {
  margin-top: 8px;
  display: flex;
  flex-direction: row;
  gap: 8px;

  .save {
    background-color: var(--c-text-green);
  }

}
</style>