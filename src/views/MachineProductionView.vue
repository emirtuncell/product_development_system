<template>
    <div>
        <v-app-bar color="primary" app dark>
            <v-toolbar-title>
                {{ machine.name }}
            </v-toolbar-title>
            <v-spacer></v-spacer>
            {{ formatDate(now) }}
        </v-app-bar>
        <v-container>
            <v-card>
                <v-card-title>
                    Üretim
                </v-card-title>
                <v-card-text>
                    <v-row class="px-8">
                        <v-spacer></v-spacer>

                        <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                                <v-icon v-bind="attrs" v-on="on" @click="showDialog()">
                                    mdi-play
                                </v-icon>
                            </template>
                            <span>Üretim Başlat</span>
                        </v-tooltip>
                    </v-row>
                    <v-data-table :items="productions" :headers="headers">
                        <template v-slot:item.start_datetime="{ item }">
                            {{ formatDate(item.start_datetime) }}
                        </template>
                        <template v-slot:item.actions="{ item }">

                            <v-tooltip bottom>
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon v-bind="attrs" v-on="on" @click="scrap_dialog = true; selected_item = item"
                                        class="mx-5">
                                        mdi-alert-remove
                                    </v-icon>
                                </template>
                                <span>Hurda Ekle</span>
                            </v-tooltip>

                            <v-tooltip bottom>
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon v-bind="attrs" v-on="on" class="mr-2"
                                        @click="stop_dialog = true; selected_item = item">
                                        mdi-stop
                                    </v-icon>
                                </template>
                                <span>Üretimi Bitir</span>
                            </v-tooltip>
                        </template>
                    </v-data-table>
                    {{ count }}

                    <v-dialog v-model="pause_dialog" width="400" persistent>
                        <v-card>
                            <v-card-title>
                                Duruş Açıkla
                            </v-card-title>
                            <v-card-text>
                                <v-select v-model="stop" :items="stops" item-text="start_datetime" item.value="id"
                                    label="Duruş" return-object>
                                    <template v-slot:selection="data">
                                        <span>{{ formatDate(data.item.start_datetime) }}</span>
                                    </template>

                                    <template v-slot:item="{ item }">
                                        <span>{{ formatDate(item.start_datetime) }}</span>
                                    </template>
                                </v-select>
                                <v-select v-model="stop.stop_cause_id" label="Duruş Sebebi" :items="stop_causes"
                                    item-text="name" item-value="id"></v-select>
                            </v-card-text>
                            <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn @click="addStop" text>Kaydet</v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>

                    <v-dialog v-model="scrap_dialog" width="400">
                        <v-card>
                            <v-card-title>
                                Hurda Ekle
                            </v-card-title>
                            <v-card-text>
                                <v-select v-model="scrap.scrap_cause_id" label="Hurda Sebebi" :items="scrap_causes"
                                    item-text="name" item-value="id"></v-select>
                                <v-text-field v-model="scrap.quantity" type="number" label="Adet"
                                    @focus="keyboardVisible = true; input = 'scrap'"></v-text-field>
                                <number-keyboard v-if="keyboardVisible && input == 'scrap'" @input="handleInput"
                                    @delete="handleDelete" @done="handleDone" />
                            </v-card-text>
                            <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn @click="scrap_dialog = false" text>İptal</v-btn>
                                <v-btn @click="addScrap" text>Kaydet</v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>

                    <v-dialog v-model="stop_dialog" width="400">
                        <v-card>
                            <v-card-title>
                                Üretimi Bitir
                            </v-card-title>
                            <v-card-text>
                                Üretimi bitirilecek, emin misiniz?
                            </v-card-text>
                            <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn @click="stop_dialog = false" text>İptal</v-btn>
                                <v-btn @click="stopProduction" text>Bitir</v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>
                    <v-dialog v-model="dialog" width="400">
                        <v-card>
                            <v-card-title>

                            </v-card-title>
                            <v-card-text>
                                <v-combobox v-model="machine_operator" :items="machine_operators" item-value="id"
                                    item-text="operator_name" :return-object="true" label="Operatör" clearable>
                                    <template v-slot:selection="data">
                                        <span>{{ data.item.operator_name }}</span>
                                    </template>
                                </v-combobox>
                                <v-combobox v-if="machine_operator" v-model="work_order" :items="work_orders"
                                    item-value="id" :return-object="true" label="İş Emri" clearable
                                    :filter="WorkOrderFilter">
                                    <template v-slot:selection="data">
                                        <span>İş Emri: {{ data.item.id }} <br>Kalıp: {{molds.find((m) => {
                                            return
                                            machine_molds.find((mo) => {
                                                return mo.id
                                                    == data.item.machine_mold_id
                                            })
                                        }).name}}
                                            <br>Planlanan Başlama: {{ formatDate(data.item.planned_start_datetime)
                                            }}</span>
                                    </template>
                                    <template v-slot:item="{ item }">
                                        <span>İş Emri: {{ item.id }} <br>Kalıp: {{molds.find((m) => {
                                            return
                                            machine_molds.find((mo) => { return mo.id == item.machine_mold_id })
                                        }).name}}
                                            <br>Planlanan Başlama: {{ formatDate(item.planned_start_datetime) }}
                                            <v-divider></v-divider></span>
                                    </template>
                                </v-combobox>

                                <v-text-field v-if="work_order" v-model="cavity_count" type="number"
                                    @focus="keyboardVisible = true; input = 'cavity'" label="Göz Adedi"></v-text-field>
                                <number-keyboard v-if="keyboardVisible && input == 'cavity'" @input="handleInput"
                                    @delete="handleDelete" @done="handleDone" />
                            </v-card-text>
                            <v-card-actions>
                                <v-spacer></v-spacer>
                                <v-btn @click="dialog = false" text>İptal</v-btn>
                                <v-btn @click="saveProduction" text :disabled="!cavity_count">Başlat</v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>
                </v-card-text>
            </v-card>
        </v-container>
    </div>
</template>

<script>
import NumberKeyboard from '@/components/NumberKeyboard.vue';
export default {
    name: 'Production',
    components: {
        NumberKeyboard
    },

    data() {
        return ({
            ws: null,
            reconnectInterval: null,
            count: null,
            input: "",
            keyboardVisible: false,
            now: new Date(),
            scrap: {},
            stop: {},
            items: [],
            machine: {},
            selected_item: {},
            work_orders: [],
            work_order: null,
            machine_operator: null,
            machine_molds: [],
            molds: [],
            machine_mold: null,
            cavity_count: null,
            machine_operators: [],
            scrap_causes: [],
            stop_causes: [],
            stops: [],
            operators: [],
            productions: [],
            type: null,
            loading: true,
            stop_dialog: false,
            scrap_dialog: false,
            pause_dialog: false,
            headers: [
                {
                    text: "İş Emri",
                    value: "work_order_id"
                },
                {
                    text: "Operatör",
                    value: "operator"
                },
                {
                    text: "Göz Adedi",
                    value: "cavity_count"
                },
                {
                    text: "Hedef",
                    value: "quantity"
                },
                {
                    text: "Başlama",
                    value: "start_datetime"
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
        handleInput(val) {
            if (this.input == "cavity") {
                this.cavity_count = this.cavity_count || ''
                this.cavity_count += val;
            }
            else if (this.input == "scrap") {
                this.scrap.quantity = this.scrap.quantity || ''
                this.scrap.quantity += val;
            }
        },
        handleDelete() {
            if (this.input == "cavity") {
                this.cavity_count = this.cavity_count || ''
                this.cavity_count = this.cavity_count.slice(0, -1);
            }
            else if (this.input == "scrap") {
                this.scrap.quantity = this.scrap.quantity || ''
                this.scrap.quantity = this.scrap.quantity.slice(0, -1);
            }
        },
        handleDone() {
            this.keyboardVisible = false;
        },
        saveProduction() {
            const production = {
                work_order_id: this.work_order.id,
                machine_operator_id: this.machine_operator.id,
                cavity_count: this.cavity_count,
                start_datetime: new Date()
            }
            this.$api.post("/productions", production).then((r) => {
                this.fetchItems()
                this.dialog = false
            }).catch((e) => {
                console.log(e.response)
            })
        },
        stopProduction() {
            this.selected_item.end_datetime = new Date()
            this.$api.put("/productions/" + this.selected_item.id, this.selected_item).then((r) => {
                console.log(r.data)
                this.fetchItems()
                this.stop_dialog = false
            }).catch((e) => {
                console.log(e.response)
            })
        },
        addScrap() {
            this.scrap.production_id = this.selected_item.id
            this.$api.post("/scraps", this.scrap).then((r) => {
                this.scrap_dialog = false
                console.log(r.data)
            }).catch((e) => {
                console.log(e.response)
            })
        },
        addStop() {
            this.stop.end_datetime = new Date();
            this.$api.put("/stops/" + this.stop.id, this.stop).then((r) => {
                this.pause_dialog = false
                console.log(r.data)
                this.fetchStops()
            }).catch((e) => {
                console.log(e.response)
            })
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
        showDialog(item) {
            if (item) {
                this.selected_item = Object.assign({}, item)
            }
            else {
                this.selected_item = {}
            }
            this.dialog = true
        },
        fetchStops() {
            this.$api.get("/stops/machine/" + this.$route.query.machine_id).then((r) => {
                this.stops = r.data
                if (this.stops.length > 0) {
                    this.pause_dialog = true
                }
            }).catch((e) => {
                console.log(e.response)
            })
        },
        fetchItems() {
            this.$api.get("/productions/machine/" + this.$route.query.machine_id).then((r) => {
                this.productions = r.data.map((p) => {
                    return ({
                        ...p,
                        quantity: this.work_orders.find((wo) => {
                            return wo.id == p.work_order_id
                        }).quantity,
                        operator: this.machine_operators.find((mo) => { return mo.id == p.machine_operator_id }).operator_name
                    })
                })
            }).catch((e) => {
                console.log(e.response)
            })
        },
        formatDate(dateString) {
            if (!dateString)
                return
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            return new Date(dateString).toLocaleDateString("tr", options) + " " + new Date(dateString).toLocaleTimeString("tr", { hour: "numeric", minute: "numeric" });
        },
        getMoldName(moldId) {
            const mold = this.molds.find((m) =>
                this.machine_molds.find((mo) => mo.id === moldId)
            );
            return mold ? mold.name : "";
        },
        WorkOrderFilter(item, queryText, itemText) {
            const moldName = this.getMoldName(item.machine_mold_id).toLowerCase();
            const workOrderId = String(item.id);
            const query = queryText.toLowerCase();

            return (
                workOrderId.includes(query) ||
                moldName.includes(query) ||
                this.formatDate(item.planned_start_datetime).toLowerCase().includes(query)
            );
        },
        connectWebSocket(token) {
            this.ws = new WebSocket(`ws://192.168.1.222:8000/productions/ws?token=${token}`);

            this.ws.onopen = () => {
                this.ws.send("");
                if (this.reconnectInterval) {
                    clearInterval(this.reconnectInterval);
                    this.reconnectInterval = null;
                }
            };

            this.ws.onmessage = (event) => {
                this.count = event.data;
            };

            this.ws.onerror = (err) => {
            };

            this.ws.onclose = () => {
                this.tryReconnect(token);
            };

        },

        tryReconnect(token) {
            if (!this.reconnectInterval) {
                this.reconnectInterval = setInterval(() => {
                    this.connectWebSocket(token);
                }, 3000);
            }
        }
    },
    mounted() {
        const token = localStorage.getItem('access_token');
        this.connectWebSocket(token);

        this.pingInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send("ping");
                this.now = new Date()
            }
        }, 10000);
        this.fetchStops()
        this.$api.get("/scrap-causes").then((r) => {
            this.scrap_causes = r.data
        }).catch((e) => {
            console.log(e.response)
        })
        this.$api.get("/stop-causes").then((r) => {
            this.stop_causes = r.data
        }).catch((e) => {
            console.log(e.response)
        })
        this.$api.get("/operators").then((r) => {
            this.operators = r.data
            this.$api.get("/molds").then((r) => {
                this.molds = r.data
                const today = new Date();
                const startDate = new Date(today);
                startDate.setDate(startDate.getDate() - 10);
                const endDate = new Date(today);
                endDate.setDate(endDate.getDate() + 20);
                const formatDate = (date) => date.toISOString().split("T")[0];
                const url = `/work-orders?start_date=${formatDate(startDate)}&end_date=${formatDate(endDate)}`;

                this.$api.get(url).then((r) => {
                    const work_orders = r.data
                    this.$api.get("/machines/" + this.$route.query.machine_id).then((r) => {
                        this.machine = r.data
                        this.$api.get("/machine-operators/machine/" + this.machine.id).then((r) => {
                            this.machine_operators = r.data.map((mo) => {
                                const operator = this.operators.find((o) => { return o.id == mo.operator_id })
                                return ({
                                    ...mo,
                                    operator_name: operator ? operator.firstname + " " + operator.lastname : ''
                                })
                            })
                        }).catch((e) => {
                            console.log(e.response)
                        })
                        this.$api.get("/machine-molds/machine/" + this.machine.id).then((r) => {
                            this.machine_molds = r.data
                            this.machine_molds.forEach((mm) => {
                                mm.mold_name = this.molds.find((m) => { return m.id == mm.mold_id }).name
                                work_orders.filter((wo) => {
                                    return wo.machine_mold_id == mm.id
                                }).forEach((i) => {
                                    this.work_orders.push(i)
                                })

                                this.fetchItems()
                            })
                        })
                    }).catch((e) => {
                        console.log(e.response)
                    })
                }).catch((e) => {
                    console.log(e.response)
                })
            }).catch((e) => {
                console.log(e.response)
            })

        }).catch((e) => {
            console.log(e.response)
        })

    },
    beforeDestroy() {
        // WebSocket bağlantısını kapat
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.close();
        }

        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }

        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
            this.reconnectInterval = null;
        }
    }
};
</script>