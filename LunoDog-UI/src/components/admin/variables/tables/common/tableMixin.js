import { toRaw } from 'vue';

export default {

  data() {return {
    pendingRows: [],
    editMode: 'table',
    pendingJson: '',
    updateKey: 0,
    pendingJsonError: false,
    isEdited: false,
  }},

  methods: {
    refresh() {
      this.updateKey += 1;
    },
    setMode(mode) {
      console.log(`setting mode to ${mode}`);
      this.isEdited = true;
      if (mode == 'json') {
        this.pendingJson = JSON.stringify(this.pendingRows, null, 2);
        this.editMode = 'json';
      } else if ( mode == 'table') {
        try {
          this.pendingRows = JSON.parse(this.pendingJson);
          if (!Array.isArray(this.pendingRows)) { throw new Error("Not an array") };
          const keysBlank = JSON.stringify(Object.keys(this.blankRow).sort());
          if (this.pendingRows.some(row => JSON.stringify(Object.keys(row).sort()) != keysBlank)) {
            throw new Error("Object structure missmatch.")
          };
          this.editMode = 'table';
          this.pendingJsonError = false;
          this.commitRows();
        } catch (error) {
          console.log(error);
          this.pendingJsonError = true
        }
      }
    },
    setValue(rowId, varName, value) {
      this.isEdited = true;
      this.pendingRows[rowId][varName] = value;
    },
    addRow() {
      this.isEdited = true;
      this.pendingRows.push({...this.blankRow});
    },
    deleteRow(index) {
      this.isEdited = true;
      console.log(index);
      this.pendingRows.splice(index, 1);
      this.refresh();
    },
    setJson(value) {
      this.pendingJson = value;
    },
    commitRows() {
      this.$emit('update:value', this.Name, this.pendingRows);
    }
  },

  mounted() {
    this.pendingRows = structuredClone(toRaw(this.initialRows));
  },

  watch: {
    initialRows(newValue, oldValue) {
      this.pendingRows = structuredClone(toRaw(this.initialRows));
      this.editMode = 'table';
      this.pendingJson = '';
      this.pendingJsonError = false;
      this.isEdited = false;
      this.refresh();
    }
  }

}