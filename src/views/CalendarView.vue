<template>
  <v-container>
    <v-sheet tile height="54" class="d-flex">
      <v-btn icon class="ma-2" @click="$refs.calendar.prev()">
        <v-icon>mdi-chevron-left</v-icon>
      </v-btn>
      <v-spacer></v-spacer>
      <v-toolbar-title v-if="$refs.calendar">
        {{ $refs.calendar.title }}
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon class="ma-2" @click="$refs.calendar.next()">
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
      <v-select v-model="type" item-value="type" item-text="name" dense hide-details style="max-width: 120px"
        class="ma-2"
        :items="[{ name: 'Gün', type: 'day' }, { name: 'Hafta', type: 'week' }, { name: 'Ay', type: 'month' }]"
        label="Görünüm"></v-select>

    </v-sheet>
    <v-calendar ref="calendar" v-model="focus" event-overlap-mode="column" :type="type" :events="events"
      interval-height="20" @click:event="getEvent" @change="fetchItems" :weekdays="weekday"></v-calendar>
    <v-dialog v-model="dialog" width="400">
      <v-card>
        <v-card-title>
          İş Emri
        </v-card-title>
        <v-card-text>
          Müşteri: {{ customer.name }}
          <v-divider></v-divider>
          Ürün: {{ product.name }}
          <v-divider></v-divider>
          Makine: {{ machine.name }}
          <v-divider></v-divider>
          Kalıp: {{ mold.name }}
          <v-divider></v-divider>
          Adet: {{ selected_item.quantity }}
          <v-divider></v-divider>
          Başlama: {{ formatDate(selected_item.planned_start_datetime) }}
          <v-divider></v-divider>
          Bitiş: {{ formatDate(selected_item.planned_end_datetime) }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="dialog = false" text>Kapat</v-btn>
          <v-btn :to="'/work-order?order_product_id=' + selected_item.order_product_id" text>İncele</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import colors from 'vuetify/lib/util/colors'
export default {
  name: 'Calendar',

  data() {
    return ({
      type: 'week',
      dialog: false,
      weekday: [1, 2, 3, 4, 5, 6, 0],
      focus: "",
      events: [],
      selected_item: {},
      machine: {},
      mold: {},
      order: {},
      product: {},
      customer: {},
      machine_molds: []
    })
  },
  methods: {
    getEvent(event) {
      this.selected_item = event.event.work_order
      Promise.all([
        this.$api.get("/machine-molds/" + event.event.work_order.machine_mold_id),
        this.$api.get("/order-products/" + event.event.work_order.order_product_id)
      ]).then(([machine_mold, order_product]) => {
        Promise.all([
          this.$api.get("/products/" + order_product.data.product_id),
          this.$api.get("/orders/" + order_product.data.order_id),
          this.$api.get("/machines/" + machine_mold.data.machine_id),
          this.$api.get("/molds/" + machine_mold.data.mold_id)
        ]).then(([product, order, machine, mold]) => {
          this.$api.get("/customers/" + order.data.customer_id).then((r) => {
            this.customer = r.data
            this.dialog = true
          }).catch((e) => {
            console.log(e.response)
          })

          this.machine = machine.data
          this.mold = mold.data
          this.order = order.data
          this.product = product.data
        }).catch((e) => {
          console.log(e.response)
        })
      }).catch((e) => {
        console.log(e.response)
      })
    },
    fetchItems() {
      this.$api.get("/work-orders?start_date=" + this.$refs.calendar.lastStart.date + "&end_date=" + this.$refs.calendar.lastEnd.date).then((r) => {
        const rawEvents = r.data.map((item) => {
          const mm = this.machine_molds.find(i => i.id == item.machine_mold_id);
          const machine_id = mm?.machine_id || 0;
          const mold_id = mm?.mold_id || 0;
          const colorNames = Object.keys(colors);
          const tones = ["accent1", "base", "darken4"];

          return {
            name: "",
            work_order: item,
            start: item.planned_start_datetime.substr(0, 16).replace("T", " "),
            end: item.planned_end_datetime.substr(0, 16).replace("T", " "),
            color: colors[colorNames[machine_id % 20]][tones[mold_id % 3]]
          }
        })
        this.events = rawEvents.sort((a, b) => {
          if (a.color < b.color) return -1;
          if (a.color > b.color) return 1;
          return 0;
        });
      })
    },
    formatDate(dateString) {
      if (!dateString)
        return
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString("tr", options) + " " + new Date(dateString).toLocaleTimeString("tr", { hour: "numeric", minute: "numeric" });
    }
  },
  computed: {

  },
  watch: {

  },
  mounted() {
    this.$refs.calendar.checkChange()
    this.$api.get("/machine-molds").then((r) => {
      this.machine_molds = r.data
      this.fetchItems();
    }).catch((e) => { console.log(e.response) })
  }
};
</script>