<template>
  <el-alert
    v-if="!serverStatus.isAvailable"
    :title="alertTitle"
    :description="alertDescription"
    type="warning"
    :closable="false"
    show-icon
    class="server-status-alert"
  >
    <div slot="title">
      <i class="el-icon-warning"></i>
      {{ alertTitle }}
    </div>
    <div>
      {{ alertDescription }}
      <el-button 
        type="text" 
        size="mini" 
        @click="recheckServer"
        :loading="checking"
        style="margin-left: 10px;"
      >
        重新检测
      </el-button>
    </div>
  </el-alert>
</template>

<script>
import { getServerInfo } from '@/utils/apiCheck'

export default {
  name: 'ServerStatus',
  data() {
    return {
      serverStatus: {
        isAvailable: true,
        baseURL: process.env.VUE_APP_BASE_API || 'http://localhost:5000',
        message: ''
      },
      checking: false
    }
  },
  computed: {
    alertTitle() {
      return '后端服务连接异常'
    },
    alertDescription() {
      return `无法连接到后端服务 (${this.serverStatus.baseURL})，请确保Flask服务已启动并监听端口5000。`
    }
  },
  mounted() {
    this.checkServerStatus()
  },
  methods: {
    async checkServerStatus() {
      this.checking = true
      try {
        this.serverStatus = await getServerInfo()
      } catch (error) {
        console.error('检查服务器状态失败:', error)
        this.serverStatus.isAvailable = false
      } finally {
        this.checking = false
      }
    },
    
    async recheckServer() {
      await this.checkServerStatus()
      if (this.serverStatus.isAvailable) {
        this.$message.success('服务器连接已恢复')
        this.$emit('server-available')
      } else {
        this.$message.error('仍无法连接到服务器')
      }
    }
  }
}
</script>

<style scoped>
.server-status-alert {
  margin-bottom: 20px;
}
</style> 