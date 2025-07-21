<template>
    <v-container>
        <v-card>
            <v-card-title>
                Üretim
            </v-card-title>
            <v-card-text>
                <v-row class="px-8">
                    <v-spacer></v-spacer>

                    <v-text-field v-model="search" ref="search" v-if="search" label="Ara..." clearable></v-text-field>

                    <v-tooltip bottom v-if="!search">
                        <template v-slot:activator="{ on, attrs }">
                            <v-icon class="mr-2" v-bind="attrs" v-on="on" @click="enableSearch">
                                mdi-magnify
                            </v-icon>
                        </template>
                        <span>Arama</span>
                    </v-tooltip>

                    <v-tooltip bottom>
                        <template v-slot:activator="{ on, attrs }">
                            <v-icon v-bind="attrs" v-on="on" @click="showDialog()">
                                mdi-plus
                            </v-icon>
                        </template>
                        <span>Yeni Ekle</span>
                    </v-tooltip>
                </v-row>

                <v-data-table :items.sync="items" :headers="headers" :search="search" :loading="loading"
                    :custom-filter="customFilter" mobile-breakpoint="0">

                    <template v-slot:item.start_datetime="{ item }">
                        {{ formatDate(item.start_datetime) }}
                    </template>
                    <template v-slot:item.end_datetime="{ item }">
                        {{ formatDate(item.end_datetime) }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                                <v-icon v-bind="attrs" v-on="on" class="mr-2"
                                    @click="selected_item = item; delete_dialog = true">
                                    mdi-delete
                                </v-icon>
                            </template>
                            <span>Sil</span>
                        </v-tooltip>

                        <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                                <v-icon v-bind="attrs" v-on="on" @click="showDialog(item)">
                                    mdi-pencil
                                </v-icon>
                            </template>
                            <span>Düzenle</span>
                        </v-tooltip>
                    </template>
                </v-data-table>
            </v-card-text>
        </v-card>
        <v-dialog v-model="dialog" width="400">
            <v-card>
                <v-card-title>
                    {{ selected_item.id ? "Düzenle" : "Yeni Ekle" }}
                </v-card-title>
                <v-card-text>
                    <v-combobox v-model="selected_item.machine_operator_id" :items="machine_operators"
                        item-text="operator_name" item-value="id" :return-object="false" label="Operatör" clearable>
                        <template v-slot:selection="data">
                            <span>{{machine_operators.find(item => data.item == item.id).operator_name}}</span>
                        </template>
                    </v-combobox>
                    <v-text-field v-model="selected_item.cavity_count" label="Göz Adedi"></v-text-field>
                    <v-text-field v-model="selected_item.start_datetime" type="datetime-local"
                        label="Başlama Tarihi"></v-text-field>
                    <v-text-field v-model="selected_item.end_datetime" type="datetime-local"
                        label="Bitiş Tarihi"></v-text-field>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn @click="dialog = false" text>İptal</v-btn>
                    <v-btn text @click="save">Kaydet</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
        <v-dialog v-model="delete_dialog" width="400">
            <v-card>
                <v-card-title>
                    Emin misiniz?
                </v-card-title>
                <v-card-text>
                    {{ selected_item.name }} silinecek!
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn @click="delete_dialog = false" text>İptal</v-btn>
                    <v-btn text @click="delete_item">Sil</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script>
export default {
    name: 'Production',

    data() {
        return ({
            items: [],
            selected_item: {},
            work_orders: [],
            work_order: {},
            machine_mold: {},
            machine_operators: [],
            operators: [],
            type: null,
            loading: true,
            headers: [
                {
                    text: "Operatör",
                    value: "machine_operator.operator_name"
                },
                {
                    text: "Göz Adedi",
                    value: "cavity_count"
                },
                {
                    text: "Başlama",
                    value: "start_datetime"
                },
                {
                    text: "Bitiş",
                    value: "end_datetime"
                },
                {
                    text: "Eylemler",
                    value: "actions",
                    align: "end",
                    sortable: false
                }
            ],
            search: "",
            dialog: false,
            delete_dialog: false
        })
    },
    methods: {
        enableSearch() {
            this.search = ' ';
            this.$nextTick(() => {
                this.$refs.search && this.$refs.search.focus();
            });
        },
        customFilter(value, search, item) {
            if (!search) return true;
            search = search.toString().toLowerCase();
            return Object.keys(item).some((key) => {
                const fieldValue = item[key];
                if (!fieldValue) return false;

                if (key === 'start_datetime' || key === 'end_datetime') {
                    const formatted = this.formatDate(fieldValue)
                    return formatted.toLowerCase().includes(search);
                }
                if (key === 'machine_operator') {
                    return fieldValue.operator_name.toLowerCase().includes(search);
                }

                return String(fieldValue).toLowerCase().includes(search);
            });
        },
        save() {

            this.selected_item.work_order_id = this.$route.query.work_order_id
            if (this.selected_item.id) {
                this.$api.put("/productions/" + this.selected_item.id, this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
            else {
                this.$api.post("/productions", this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
        },
        delete_item() {
            this.$api.delete("/productions/" + this.selected_item.id).then((r) => {
                this.delete_dialog = false
                this.fetchItems()
            }).catch((e) => {
                console.log(e.response)
            })
        },
        showDialog(item) {
            if (item) {
                this.selected_item = Object.assign({}, item)
            }
            else {
                this.selected_item = {}
            }
            this.dialog = true
        },
        fetchItems() {
            this.$api.get("/productions/work-order/" + this.$route.query.work_order_id).then((r) => {

                this.loading = false
                this.items = r.data.map(item => {
                    const machine_operator = this.machine_operators.find(mo => mo.id === item.machine_operator_id);
                    return {
                        ...item,
                        machine_operator: machine_operator ? machine_operator : ''
                    }
                });
            }).catch((e) => {
                console.log(e.response)
            })
        },
        formatDate(dateString) {
            if (!dateString)
                return
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            return new Date(dateString).toLocaleDateString("tr", options) + " " + new Date(dateString).toLocaleTimeString("tr", { hour: "numeric", minute: "numeric" });
        }
    },
    mounted() {
        this.$api.get("/operators").then((r) => {
            this.operators = r.data
            this.$api.get("/work-orders/" + this.$route.query.work_order_id).then((r) => {
                this.work_order = r.data
                this.$api.get("/machine-molds/" + this.work_order.machine_mold_id).then((r) => {
                    this.machine_mold = r.data
                    this.$api.get("/machine-operators/machine/" + this.machine_mold.machine_id).then((r) => {
                        this.machine_operators = r.data
                        this.machine_operators.forEach((mo) => {
                            const op = this.operators.find((o) => { return o.id == mo.operator_id })
                            mo.operator_name = op.firstname + " " + op.lastname
                        })
                        this.fetchItems()
                    }).catch((e) => {
                        console.log(e)
                    })
                }).catch((e) => {
                    console.log(e)
                })
            }).catch((e) => {
                console.log(e.response)
            })
        }).catch((e) => {
            console.log(e.response)
        })
    }
};
</script>