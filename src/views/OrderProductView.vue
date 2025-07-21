<template>
    <v-container>
        <v-card>
            <v-card-title>
                Sipariş Ürün
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

                <v-data-table :items="items" :headers="headers" :search="search" :loading="loading"
                    mobile-breakpoint="0">

                    <template v-slot:item.planned="{ item }">
                        <v-chip v-if="item.planned">Evet</v-chip>
                    </template>
                    <template v-slot:item.actions="{ item }">

                        <v-tooltip bottom>
                            <template v-slot:activator="{ on, attrs }">
                                <v-badge dot left v-if="!item.work_orders.length && item.planned">
                                    <v-icon v-bind="attrs" v-on="on" class="mr-2"
                                        @click="$router.push('/work-order?order_product_id=' + item.id).catch(() => { })">
                                        mdi-cog
                                    </v-icon>
                                </v-badge>

                                <v-icon v-bind="attrs" v-on="on" class="mr-2" v-else
                                    @click="$router.push('/work-order?order_product_id=' + item.id).catch(() => { })">
                                    mdi-cog
                                </v-icon>
                            </template>
                            <span>İş Emirleri</span>
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
                    <v-combobox v-model="selected_item.product_id" :items="products" item-text="name" item-value="id"
                        :return-object="false" label="Ürün" clearable>
                        <template v-slot:selection="data">
                            <span>{{products.find(item => data.item == item.id).name}}</span>
                        </template>
                    </v-combobox>
                    <v-text-field v-model="selected_item.quantity" label="Miktar"></v-text-field>
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
    name: 'OrderProduct',

    data() {
        return ({
            items: [],
            products: [],
            selected_item: {},
            loading: true,
            headers: [
                {
                    text: "Ürün",
                    value: "product_name"
                },
                {
                    text: "Miktar",
                    value: "quantity"
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
            this.selected_item.order_id = this.$route.query.order_id
            if (this.selected_item.id) {
                this.$api.put("/order-products/" + this.selected_item.id, this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
            else {
                this.$api.post("/order-products", this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
        },
        delete_item() {
            this.$api.delete("/order-products/" + this.selected_item.id).then((r) => {
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
        async fetchItems() {
            try {
                const r = await this.$api.get("/order-products/order/" + this.$route.query.order_id);

                const itemsWithWorkOrders = await Promise.all(r.data.map(async (item) => {
                    const response = await this.$api.get("/work-orders/order-product/" + item.id);
                    const product = this.products.find(m => m.id === item.product_id);
                    // Gerekirse response.data'dan da iş emri bilgisi ekleyebilirsin
                    return {
                        ...item,
                        product_name: product ? product.name : '',
                        work_orders: response.data
                    };
                }));

                this.items = itemsWithWorkOrders;
            } catch (e) {
                console.log(e.response);
            } finally {
                this.loading = false;
            }
        }
    },
    mounted() {
        this.$api.get("/products").then((r) => {
            this.products = r.data
            this.fetchItems()
        }).catch((e) => {
            console.log(e.response)
        })
    }
};
</script>