<template>
    <v-container>
        <v-card>
            <v-card-title>
                İş Emirleri
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

                <v-data-table :items="items" :headers="headers" :search="search" :custom-filter="customFilter"
                    :loading="loading" mobile-breakpoint="0">
                    <template v-slot:item.planned_start_datetime="{ item }">
                        {{ formatDate(item.planned_start_datetime) }}
                    </template>
                    <template v-slot:item.planned_end_datetime="{ item }">
                        {{ formatDate(item.planned_end_datetime) }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                        
                        <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                                <v-icon v-bind="attrs" v-on="on" class="mr-2"
                                    @click="$router.push('/production?work_order_id='+item.id).catch((e)=>{})">
                                    mdi-robot-industrial
                                </v-icon>
                            </template>
                            <span>Üretim</span>
                        </v-tooltip>

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
                    <v-combobox v-model="selected_item.machine_mold_id" :items="machineMolds" item-text="machine_mold_name" item-value="id"
                        :return-object="false" label="Makine Kalıp" clearable>
                        <template v-slot:selection="data">
                            <span>{{machine_molds.find(item => data.item == item.id).machine_mold_name}}</span>
                        </template>
                    </v-combobox>
                    <v-text-field v-model="selected_item.quantity" label="Miktar"></v-text-field>
                    <v-text-field v-model="selected_item.planned_start_datetime" type="datetime-local"
                        label="Planlanan Başlama Tarihi"></v-text-field>
                    <v-text-field v-model="selected_item.planned_end_datetime" type="datetime-local"
                        label="Planlanan Bitiş Tarihi"></v-text-field>
                    <v-alert v-if="selected_item.machine_mold_id && calculatedTime" type="info" class="my-3">
                        Hesaplanan Üretim Süresi: <strong>{{ calculatedTime }}</strong> dakika
                    </v-alert>
                    <v-alert v-if="selected_item.planned_end_datetime && selected_item.planned_start_datetime"
                        type="info" class="my-3">
                        Planlanan Üretim Süresi: <strong>{{ (new Date(selected_item.planned_end_datetime) - new
                            Date(selected_item.planned_start_datetime)) / (1000 * 60) }}</strong> dakika
                    </v-alert>
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
        <v-dialog v-model="alertDialog">
            <v-card>
                <v-card-title>

                </v-card-title>
                <v-card-text>
                    <v-alert type="error" v-for="item,i in alertMessages.machine_conflicts" :key="i">
                        Bu makineye
                        {{ formatDate(item.conflict_start) }} ile {{ formatDate(item.conflict_end) }} tarihleri arasında başka kalıp takılması planlanmış! 
                        <v-btn @click="$router.push('/work-order?order_product_id='+item.order_product_id).catch(()=>{});location.reload()" text>İncele</v-btn>
                    </v-alert>
                    <v-alert type="error" v-for="item,i in alertMessages.mold_conflicts" :key="i">
                        Bu kalıbın
                        {{ formatDate(item.conflict_start) }} ile {{ formatDate(item.conflict_end) }} tarihleri arasında başka makineye takılması planlanmış! 
                        <v-btn @click="$router.push('/work-order?order_product_id='+item.order_product_id).catch(()=>{});location.reload()" text>İncele</v-btn>
                    </v-alert>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn @click="alertDialog=false" text>Kapat</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script>
export default {
    name: 'WorkOrder',

    data() {
        return ({
            items: [],
            machine_molds: [],
            machines: [],
            molds: [],
            selected_item: {},
            loading: true,
            alertDialog:false,
            alertMessages:{},
            order_product: {},
            work_orders: [],
            location:location,
            headers: [
                {
                    text: "Makine Kalıp",
                    value: "machine_mold_name"
                },
                {
                    text: "Miktar",
                    value: "quantity"
                },
                {
                    text: "Planlanan Başlama",
                    value: "planned_start_datetime"
                },
                {
                    text: "Planlanan Bitiş",
                    value: "planned_end_datetime"
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

                if (key === 'planned_start_datetime' || key === 'planned_end_datetime') {
                    const formatted = this.formatDate(fieldValue)
                    return formatted.toLowerCase().includes(search);
                }

                return String(fieldValue).toLowerCase().includes(search);
            });
        },
        save() {
            this.selected_item.order_product_id = this.$route.query.order_product_id
            if (this.selected_item.id) {
                this.$api.put("/work-orders/" + this.selected_item.id, this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                    
                    if(e.response.data.detail){
                        this.alertMessages=e.response.data.detail
                        this.alertDialog=true
                    }
                })
            }
            else {
                this.$api.post("/work-orders", this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                    
                    if(e.response.data.detail){
                        this.alertMessages=e.response.data.detail
                        this.alertDialog=true
                    }
                })
            }
        },
        delete_item() {
            this.$api.delete("/work-orders/" + this.selected_item.id).then((r) => {
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
                this.selected_item = { machine_mold_id: null}
            }
            this.dialog = true
        },
        fetchItems() {
            this.$api.get("/work-orders/order-product/" + this.$route.query.order_product_id).then((r) => {
                this.loading = false
                this.items = r.data.map(item => {
                    const machine_mold = this.machine_molds.find(m => m.id === item.machine_mold_id);
                    item.planned_start_datetime=item.planned_start_datetime.substr(0,16)
                    item.planned_end_datetime=item.planned_end_datetime.substr(0,16)
                    return {
                        ...item,
                        machine_mold_name: machine_mold ? machine_mold.machine.name + ' - ' + machine_mold.mold.name : '',
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
    computed: {
        machineMolds() {
            const machineMap = Object.fromEntries(this.machines.map(m => [m.id, m]))
            const moldMap = Object.fromEntries(this.molds.map(m => [m.id, m]))

            return this.machine_molds.map((mm) => {
                const machine = machineMap[mm.machine_id]
                const mold = moldMap[mm.mold_id]

                return {
                    ...mm,
                    machine_mold_name: (machine ? machine.name : null) + ' - ' + (mold ? mold.name : null),
                    machine: machine || null,
                    mold: mold || null
                }
            })
        },
        calculatedTime() {
            if (!this.selected_item.machine_mold_id) {
                return null;
            }
            const machineMold = this.machine_molds.filter((i) => {
                return i.id == this.selected_item.machine_mold_id
            })[0]
            if (!machineMold) {
                return null;
            }
            const productMold = this.mold_products.find(pm => pm.mold_id === machineMold.mold_id);
            const calculatedTime = (this.selected_item.quantity * machineMold.cycle_time / (productMold.count * 60)) + machineMold.setup_time;
            return Math.round(calculatedTime);
        }
    },
    mounted() {

        this.$api.get("/order-products/" + this.$route.query.order_product_id).then((res) => {
            this.order_product = res.data
            const productId = res.data.product_id;

            this.$api.get("/mold-products/product/" + productId).then((res) => {
                this.mold_products = res.data
                const moldProducts = res.data;

                moldProducts.forEach((moldProduct) => {
                    this.$api.get("/machine-molds/mold/" + moldProduct.mold_id).then((res) => {
                        const machineMolds = res.data;

                        machineMolds.forEach((mm) => {
                            Promise.all([
                                this.$api.get("/machines/" + mm.machine_id),
                                this.$api.get("/molds/" + mm.mold_id)
                            ]).then(([machineRes, moldRes]) => {
                                const machine = machineRes.data;
                                const mold = moldRes.data;
                                this.machine_molds.push({
                                    ...mm,
                                    machine: machine,
                                    mold: mold,
                                    machine_mold_name: `${machine.name} - ${mold.name}`
                                });

                                this.machines.push(machine);
                                this.molds.push(mold);

                                this.fetchItems();
                            })
                                .catch((e) => console.log(e));
                        });
                    }).catch((e) => console.log(e));
                });
            }).catch((e) => console.log(e));
        }).catch((e) => console.log(e));
    }
};
</script>