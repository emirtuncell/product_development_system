<template>
    <v-container>
        <v-card>
            <v-card-title>
                Kalıp Ürün
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
                    <v-combobox v-model="selected_item.product_id" :items="products" item-text="name" item-value="id"
                        :return-object="false" label="Ürün" clearable v-if="type != 'product'">
                        <template v-slot:selection="data">
                            <span>{{products.find(item => data.item == item.id).name}}</span>
                        </template>
                    </v-combobox>
                    <v-combobox v-model="selected_item.mold_id" :items="molds" item-text="name" item-value="id"
                        :return-object="false" label="Kalıp" clearable v-if="type != 'mold'">
                        <template v-slot:selection="data">
                            <span>{{molds.find(item => data.item == item.id).name}}</span>
                        </template>
                    </v-combobox>
                    <v-text-field v-model="selected_item.count" label="Göz Adedi"></v-text-field>
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
    name: 'MoldProduct',

    data() {
        return ({
            items: [],
            selected_item: {},
            molds: [],
            products: [],
            type: null,
            loading:true,
            headers: [
                {
                    text: "Kalıp",
                    value: "mold_name"
                },
                {
                    text: "Ürün",
                    value: "product_name"
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

            if (this.type == 'mold') {
                this.selected_item.mold_id = this.$route.query.mold_id
            }
            else if (this.type == 'product') {
                this.selected_item.product_id = this.$route.query.product_id
            }
            if (this.selected_item.id) {
                this.$api.put("/mold-products/" + this.selected_item.id, this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
            else {
                this.$api.post("/mold-products", this.selected_item).then((r) => {
                    this.fetchItems()
                    this.dialog = false
                }).catch((e) => {
                    console.log(e.response)
                })
            }
        },
        delete_item() {
            this.$api.delete("/mold-products/" + this.selected_item.id).then((r) => {
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
            if (this.$route.query.product_id) {
                query = "/product/" + this.$route.query.product_id
                this.type = "product"
            }
            else if (this.$route.query.mold_id) {
                query = "/mold/" + this.$route.query.mold_id
                this.type = "mold"
            }
            this.$api.get("/mold-products" + query).then((r) => {
                
                this.loading=false
                this.items = r.data.map(item => {
                    // Her item'da mold_id ve product_id'yi kullanarak isimleri alıyoruz
                    const mold = this.molds.find(m => m.id === item.mold_id);
                    const product = this.products.find(m => m.id === item.product_id);
                    return {
                        ...item,
                        mold_name: mold ? mold.name : '',
                        product_name: product ? product.name : ''
                    }
                });
            }).catch((e) => {
                console.log(e.response)
            })
        }
    },
    mounted() {
        this.$api.get("/molds").then((r) => {
            this.molds = r.data
            this.$api.get("/products").then((r) => {
                this.products = r.data
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