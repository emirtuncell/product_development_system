<template>
    <v-container>
        <v-card>
            <v-card-title>
                Siparişler
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
                    <template v-slot:item.order_datetime="{ item }">
                        {{ formatDate(item.order_datetime) }}
                    </template>
                    <template v-slot:item.deadline_datetime="{ item }">
                        {{ formatDate(item.deadline_datetime) }}
                    </template>
                    <template v-slot:item.actions="{ item }">

                        <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                                <v-badge :content="item.order_products.length" left v-if="item.order_products.length">
                                    <v-icon v-bind="attrs" v-on="on" class="mr-2"
                                        @click="$router.push('/order-product?order_id=' + item.id).catch(() => { })">
                                        mdi-cart-minus
                                    </v-icon>
                                </v-badge>
                                <v-badge v-else left dot>
                                    <v-icon v-bind="attrs" v-on="on" class="mr-2"
                                        @click="$router.push('/order-product?order_id=' + item.id).catch(() => { })">
                                        mdi-cart-minus
                                    </v-icon>
                                </v-badge>
                            </template>
                            <span>Sipariş Ürünleri</span>
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
                    <v-text-field type="datetime-local" v-model="selected_item.order_datetime"
                        label="Sipariş Tarihi"></v-text-field>
                    <v-text-field type="datetime-local" v-model="selected_item.deadline_datetime"
                        label="Teslim Tarihi"></v-text-field>
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
    name: 'Order',

    data() {
        return ({
            items: [],
            customers: [],
            selected_item: {},
            loading: true,
            headers: [
                {
                    text: "Sipariş Tarihi",
                    value: "order_datetime"
                },
                {
                    text: "Teslim Tarihi",
                    value: "deadline_datetime"
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

                if (key === 'order_datetime' || key === 'deadline_datetime') {
                    const formatted = this.formatDate(fieldValue)
                    return formatted.toLowerCase().includes(search);
                }

                return String(fieldValue).toLowerCase().includes(search);
            });
        },
        save() {
            this.selected_item.customer_id = this.$route.query.customer_id
            if (this.selected_item.id) {
                this.$api.put("/orders/" + this.selected_item.id, this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
            else {
                this.$api.post("/orders", this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
        },
        delete_item() {
            this.$api.delete("/orders/" + this.selected_item.id).then((r) => {
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
                this.selected_item = {order_datetime:new Date().toLocaleString('sv-SE', { hour12: false }).replace(' ', 'T').slice(0, 16)}
            }
            this.dialog = true
        },
        async fetchItems() {
            try {
                const r = await this.$api.get("/orders/customer/" + this.$route.query.customer_id);

                const enrichedItems = await Promise.all(r.data.map(async (item) => {
                    const customer = this.customers.find(m => m.id === item.customer_id);

                    // order-product'ları çek
                    const orderProductsRes = await this.$api.get("/order-products/order/" + item.id);

                    return {
                        ...item,
                        customer_name: customer ? customer.name : '',
                        order_products: orderProductsRes.data,  // içine göm
                    };
                }));

                this.items = enrichedItems;
            } catch (e) {
                console.log(e.response);
            } finally {
                this.loading = false;
            }
        },
        formatDate(dateString) {
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            return new Date(dateString).toLocaleDateString("tr", options) + " " + new Date(dateString).toLocaleTimeString("tr", { hour: "numeric", minute: "numeric" });
        }
    },
    mounted() {
        this.$api.get("/customers").then((r) => {
            this.customers = r.data
            this.fetchItems()
        }).catch((e) => {
            console.log(e.response)
        })
    }
};
</script>