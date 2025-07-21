<template>
  <v-snackbar :color="$message.color" v-model="$message.show" app>
    {{ $message.text }}
    <template v-slot:action="{ attrs }">
      <v-btn color="white" icon v-bind="attrs" @click="closeMessage"><v-icon>mdi-close</v-icon></v-btn>
    </template>
  </v-snackbar>
</template>

<script>
export default({
  name: "MessageComponent",
  methods: {
    closeMessage() {
      this.$set(this.$message, 'show', false);
    }
  }
});
</script>
