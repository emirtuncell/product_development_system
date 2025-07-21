<template>
    <v-container>
        <h2>Dinamik Component</h2>
        <component v-if="dynamicComponent" :is="dynamicComponent" />
        <v-alert v-else type="info">Bileşen yükleniyor...</v-alert>
    </v-container>
</template>

<script>
// Bu sürüm compiler içerir
import Vue from 'vue/dist/vue.esm.js'

export default {
    name: 'CustomComponent',
    data() {
        return {
            dynamicComponent: null
        }
    },
    mounted() {
        this.dynamicComponent = this.createDynamicComponent()
    },
    methods: {
        test() {
            console.log("OK")
        },
        createDynamicComponent() {
            const compiled = Vue.compile(`
        <v-card class="pa-4">
            <v-card-title>Selam</v-card-title>
                <v-card-text>
                    Deneme
                    </v-card-text>
                    <v-card-actions><v-btn color="primary" @click="sayHello">Tıkla</v-btn></v-card-actions>
        </v-card>
      `)

            // Script kısmı değerlendiriliyor
            let componentOptions = {}
            try {
                const exports = {}
                eval(`exports.default = {
          methods: {
            sayHello() {
              console.log(this.$parent)
            }
          }
        }`)
                componentOptions = exports.default
            } catch (err) {
                console.error('Script parsing error:', err)
            }

            // Derlenmiş template + metotlar birleştiriliyor
            return {
                ...componentOptions,
                render: compiled.render,
                staticRenderFns: compiled.staticRenderFns
            }
        }
    }
}
</script>
