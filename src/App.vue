<template>
  <v-app>
    <v-app-bar app color="primary" dark v-if="$route.name != 'machine_production' && $isLogin.value">
      <v-app-bar-nav-icon class="d-md-none" @click="drawer = !drawer"></v-app-bar-nav-icon>
      <div class="d-none d-md-flex">
        <v-btn v-for="item, i in items" :key="i" text :to="item.to">{{ item.text }}</v-btn>
      </div>
      <v-btn @click="logout" text>Çıkış</v-btn>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer" app temporary left>
      <v-list nav>
        <v-list-item-group>
          <v-list-item v-for="(i, j) in items" :key="j" :to="i.to">
            <v-list-item-icon>
              <v-icon>{{ i.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ i.text }}</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
      <v-divider></v-divider>
      <v-btn @click="logout" text><v-icon>mdi-logout</v-icon> Çıkış</v-btn>
    </v-navigation-drawer>
    <v-main>
      <router-view />
    </v-main>
    <message-component />
  </v-app>
</template>

<script>
import MessageComponent from './components/MessageComponent.vue';

export default {
  name: 'App',
  components: {
    MessageComponent
  },
  data() {
    return ({
      drawer: false,
      items: [
        {
          text: "Makineler",
          to: "/machine",
          icon: "mdi-robot-industrial"
        },
        {
          text: "Kalıplar",
          to: "/mold",
          icon: "mdi-blur-linear"
        },
        {
          text: "Operatörler",
          to: "/operator",
          icon: "mdi-account"
        },
        {
          text: "Ürünler",
          to: "/product",
          icon: "mdi-package-variant"
        },
        {
          text: "Müşteriler",
          to: "/customer",
          icon: "mdi-account-multiple"
        },
        {
          text: "Takvim",
          to: "/calendar",
          icon: "mdi-calendar"
        },
        {
          text: "Duruş",
          to: "/stop-cause",
          icon: "mdi-wrench-clock"
        },
        {
          text: "Hurda",
          to: "/scrap-cause",
          icon: "mdi-package-variant-closed-remove"
        },
        {
          text: "Kullanıcı",
          to: "/user",
          icon: "mdi-account-key"
        }
      ]
    })
  },
  methods: {
    logout() {
      localStorage.removeItem("access_token");
      this.$isLogin.value = false;
      this.$router.push("/login").catch((e) => { console.log(e) });
    }
  },
  mounted() {
    this.$api.get("/auth/me").then((r) => {
      this.$isLogin.value = true;
    }).catch((e) => {
      this.$router.push("/login").catch((e) => { console.log(e) })
    })
  }
};
</script>

<style>
.w-100 {
  width: 100%;
}

* {
  text-transform: none !important;
}
</style>