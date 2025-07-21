import Vue from 'vue';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';
import { tr } from 'vuetify/es5/locale'; // Burada 'tr' dil dosyasını doğru şekilde import ediyoruz

Vue.use(Vuetify);

const vuetify = new Vuetify({
  lang: {
    locales: { tr }, // Türkçe dil desteğini ekleyin
    current: 'tr',    // Varsayılan dil olarak Türkçe seçin
  },
});

export default vuetify;
