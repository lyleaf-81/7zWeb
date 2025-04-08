import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import axios from 'axios';

// 设置 axios 的基础 URL
axios.defaults.baseURL = 'http://192.168.1.165:5000';

// 将 axios 挂载到 Vue 的原型上，使可以在全局使用 this.$http 访问 axios
Vue.prototype.$http = axios;

// 关闭生产提示信息
Vue.config.productionTip = false;

// 使用 ElementUI 插件
Vue.use(ElementUI);

// 创建并挂载 Vue 实例到 #app 元素上
new Vue({
  render: h => h(App),
}).$mount('#app')