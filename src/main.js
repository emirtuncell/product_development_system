import Vue from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import api from './api'


Vue.config.productionTip = false
Vue.prototype.$api = api
Vue.prototype.$message = Vue.observable({
  show: false,
  text: "text",
  color: "primary"
});
Vue.prototype.$isLogin = Vue.observable({ value: false });

new Vue({
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app')
