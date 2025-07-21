<template>
    <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
            <v-col cols="12" sm="8" md="6" lg="4">
                <v-form v-model="valid" @submit.prevent="valid ? login : null">
                    <v-card elevation="10" class="pa-4">
                        <v-card-title class="text-h4 justify-center">
                            <v-spacer></v-spacer>
                            PDS
                            <v-spacer></v-spacer>
                        </v-card-title>
                        <v-card-text>
                            <v-text-field v-model="user.username" label="Kullanıcı Adı"
                                prepend-icon="mdi-account"></v-text-field>
                            <v-text-field v-model="user.password" :type="show_password ? 'text' : 'password'"
                                label="Parola" prepend-icon="mdi-lock"
                                :append-icon="show_password ? 'mdi-eye' : 'mdi-eye-off'"
                                @click:append="show_password = !show_password"
                                autocomplete="password"
                                @keyup="checkCapsLock" :hint="capslock_on?'Caps Lock açık!':''" />
                        </v-card-text>
                        <v-card-actions>
                            <v-spacer></v-spacer>
                            <v-btn @click="login" :disabled="!valid" text color="primary" type="submit">Giriş</v-btn>
                            <v-spacer></v-spacer>
                        </v-card-actions>
                    </v-card>
                </v-form>
            </v-col>
        </v-row>
    </v-container>

</template>

<script>
export default {
    name: 'Login',

    data() {
        return ({
            user: {},
            dialog: true,
            valid: false,
            show_password: false,
            capslock_on: false
            
            
        })
    },
   methods: {
    login() {
        this.$api.post("/auth/login", this.user).then((r) => {
            localStorage.setItem("access_token", r.data.access_token)
            this.$router.push("/").catch((e)=>{console.log(e)})
            this.$isLogin.value=true;
        }).catch((e) => {
            this.$message.text="Hata!"
            this.$message.color="error"
            this.$message.show=true
        })
    
    },
    checkCapsLock(e) {
        this.capslock_on = e.getModifierState && e.getModifierState("CapsLock");
    }
},
mounted() {
}

};
</script>