<template>
  <v-card class="pa-2" outlined>
    <v-row>
      <v-col v-for="n in 9" :key="n" cols="4">
        <v-btn block @click="$emit('input', n.toString())">{{ n }}</v-btn>
      </v-col>
      <v-col cols="4">
        <v-btn block @click="$emit('input', '0')">0</v-btn>
      </v-col>
      <v-col cols="4">
        <v-btn block @click="$emit('delete')">←</v-btn>
      </v-col>
      <v-col cols="4">
        <v-btn block color="primary" @click="$emit('done')">Tamam</v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>


<script>
export default ({
    name: "NumberKeyboard"
})


</script>