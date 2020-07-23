import Vue from 'vue'
import {BootstrapVue, BootstrapVueIcons} from 'bootstrap-vue'
import VueRouter from 'vue-router'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import App from './App.vue'
import routes from './routes'

Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons )
Vue.use(VueRouter)

Vue.config.productionTip = false
Vue.config.devtools = true

const router = new VueRouter({
  routes // short for `routes: routes`
})

new Vue({
  router,
  render: h=> h(App)
}).$mount('#app')