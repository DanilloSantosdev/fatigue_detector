<template>
  <v-app>
    <v-app-bar color="primary" prominent>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-toolbar-title class="text-h5 font-weight-bold">
        <v-icon start>mdi-car-emergency</v-icon>
        Sistema de Detecção de Fadiga
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn icon>
        <v-icon>mdi-bell</v-icon>
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" temporary>
      <v-list>
        <v-list-item 
          prepend-icon="mdi-view-dashboard" 
          title="Dashboard" 
          value="dashboard"
          :to="{ name: 'Dashboard' }"
        ></v-list-item>

        <v-list-item 
          prepend-icon="mdi-file-document" 
          title="Relatórios" 
          value="reports"
          :to="{ name: 'Reports' }"
        ></v-list-item>

        <v-list-item 
          prepend-icon="mdi-car-cog" 
          title="Veículos" 
          value="vehicles"
          :to="{ name: 'Vehicles' }"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'

const drawer = ref(false)
</script>

<style scoped>
/* Estilos globais podem ser adicionados aqui */
</style>

