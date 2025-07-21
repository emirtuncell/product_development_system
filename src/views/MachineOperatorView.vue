<template>
    <v-container>
        <v-card>
            <v-card-title>
                Makine Operatör
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

                <v-data-table :items.sync="items" :headers="headers" :search="search" :loading="loading"  mobile-breakpoint="0">
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
                    <v-combobox v-model="selected_item.machine_id" :items="machines" item-text="name" item-value="id"
                        :return-object="false" label="Makine" clearable v-if="type != 'machine'">
                        <template v-slot:selection="data">
                            <span>{{machines.find(item => data.item == item.id).name}}</span>
                        </template>
                    </v-combobox>
                    <v-combobox v-model="selected_item.operator_id" :items="operators" item-value="id"
                        :return-object="false" label="Operator" clearable v-if="type != 'operator'">
                        <template v-slot:selection="data">
                            <span>{{operators.find(item => data.item == item.id).firstname}} {{
                                operators.find(item =>data.item==item.id).lastname }}</span>
                        </template>
                        <template v-slot:item="{ item }">
                            <div>{{ item.firstname }} {{ item.lastname }}</div>
                        </template>
                    </v-combobox>
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
    name: 'MachineOperator',

    data() {
        return ({
            items: [],
            selected_item: {},
            machines: [],
            operators: [],
            type: null,
            loading:true,
            headers: [
                {
                    text: "Makine",
                    value: "machine_name"
                },
                {
                    text: "Operator",
                    value: "operator_name"
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
        save() {
            if (this.type == 'machine') {
                this.selected_item.machine_id = this.$route.query.machine_id
            }
            else if (this.type == 'operator') {
                this.selected_item.operator_id = this.$route.query.operator_id
            }
            if (this.selected_item.id) {
                this.$api.put("/machine-operators/" + this.selected_item.id, this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
            else {
                this.$api.post("/machine-operators", this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
        },
        delete_item() {
            this.$api.delete("/machine-operators/" + this.selected_item.id).then((r) => {
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

            var query = ""
            if (this.$route.query.machine_id) {
                query = "/machine/" + this.$route.query.machine_id
                this.type = "machine"
            }
            else if (this.$route.query.operator_id) {
                query = "/operator/" + this.$route.query.operator_id
                this.type = "operator"
            }
            this.$api.get("/machine-operators" + query).then((r) => {
                this.loading=false
                this.items = r.data.map(item => {
                    // Her item'da machine_id ve operator_id'yi kullanarak isimleri alıyoruz
                    const machine = this.machines.find(m => m.id === item.machine_id);
                    const operator = this.operators.find(m => m.id === item.operator_id);

                    return {
                        ...item,
                        machine_name: machine ? machine.name : '',
                        operator_name: operator ? operator.firstname + " " + operator.lastname : ''
                    }
                });
            }).catch((e) => {
                console.log(e.response)
            })
        }
    },
    mounted() {
        this.$api.get("/machines").then((r) => {
            this.machines = r.data
            this.$api.get("/operators").then((r) => {
                this.operators = r.data
                this.fetchItems()
            }).catch((e) => {
                console.log(e.response)
            })
        }).catch((e) => {
            console.log(e.response)
        })

    }
};
</script>