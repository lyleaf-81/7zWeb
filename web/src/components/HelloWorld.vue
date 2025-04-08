HelloWorld.vue (1-1)


<template>
  <div class="container" >
    <el-card class="file-card">
      <template #header>
        <div class="card-header">
          <span>文件列表</span>
          <el-button 
            type="primary" 
            size="mini"
            @click="loadFiles"
            :loading="loading"
          >刷新列表</el-button>
        </div>
      </template>
      <!-- 目录导航 -->
    <div class="directory-nav">
      <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item 
          v-for="(pathPart, index) in pathParts"
          :key="index"
          :to="getBreadcrumbLink(index)"
        >
          {{ pathPart || '根目录' }}
        </el-breadcrumb-item>
      </el-breadcrumb>
      
      <el-button 
        v-if="currentPath !== ''"
        type="text" 
        icon="el-icon-arrow-left"
        @click="goUp"
        title="返回上一级"
      ></el-button>
    </div>
     <!-- 目录列表 -->
     <el-card class="directory-card">
      <el-table
    :data="fileData.directories"
    @row-click="enterDirectory"
  >
    <el-table-column label="目录信息" min-width="300">
      <template #default="{row}">
        <div class="directory-info">
          <i class="el-icon-folder"></i>
          <div class="meta">
            <div class="name">{{ row.name }}</div>
            <div class="details">
              {{ row.file_count }}个文件 / {{ formatSize(row.size) }}
            </div>
          </div>
        </div>
      </template>
    </el-table-column>
    <el-table-column label="修改时间" width="180">
      <template #default="{row}">
        {{ formatDate(row.mtime) }}
      </template>
    </el-table-column>
  </el-table>
    </el-card>

      <!-- 普通文件列表 -->
      <el-table
        :data="fileData.files.singleFiles"
        @row-contextmenu="handleContextMenu"
        v-loading="loading"
        stripe
      >
        <el-table-column prop="name" label="文件名" min-width="300">
          <template #default="{row}">
            <i class="el-icon-document" style="margin-right: 8px"></i>
            <el-tooltip :content="row.name" placement="top">
              <span class="filename">{{ row.name }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        
        <el-table-column label="大小" width="120">
          <template #default="{row}">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>

        <el-table-column label="修改时间" width="180">
          <template #default="{row}">
            {{ formatDate(row.mtime) }}
          </template>
        </el-table-column>

         <!-- 文件列表列添加删除按钮 -->
  <el-table-column label="操作" width="120">
    <template #default="{row}">
      <el-button
        type="text"
        @click="startExtract(row)"
        icon="el-icon-folder-opened"
        title="解压文件"
      ></el-button>
      <el-button
        type="text"
        icon="el-icon-delete"
        class="delete-btn"
        title="删除文件"
        @click="confirmDelete(row)"
      ></el-button>
    </template>
  </el-table-column>
      </el-table>

      <!-- 分卷包列表 -->
      <el-divider content-position="left"><i class="el-icon-files"></i> 分卷压缩包</el-divider>
      <el-table
        :data="fileData.files.volumeGroups"
        @row-contextmenu="handleContextMenu"
        row-class-name="volume-row"
      >
        <el-table-column label="分卷包名称" min-width="300">
          <template #default="{row}">
            <i class="el-icon-files" style="margin-right: 8px; color: #409EFF"></i>
            <el-tooltip :content="row.base_name" placement="top">
              <span class="filename">{{ row.base_name }}</span>
            </el-tooltip>
          </template>
        </el-table-column>

        <!-- <el-table-column label="分卷数量" width="120">
          <template #default="{row}">
            <el-tag type="info">{{ row.part_count }}个分卷</el-tag>
          </template>
        </el-table-column> -->

        <el-table-column label="总大小" width="120">
          <template #default="{row}">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120">
          <template #default="{row}">
            <el-button
              type="primary"
              icon="el-icon-folder-opened"
              @click="startExtractVolume(row)"
              size="mini"
            >解压分卷</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 解压任务列表 -->
    <el-card class="task-card">
      <template #header>
        <span>解压任务</span>
        <el-tag type="info">自动刷新间隔：2秒</el-tag>
      </template>

      <el-table :data="tasks" :row-class-name="taskRowStyle">
        <el-table-column label="文件名" prop="filename" min-width="300"></el-table-column>
        
        <el-table-column label="进度" min-width="300">
          <template #default="{row}">
            <el-progress 
              :percentage="row.progress"
              :status="getStatus(row.status)"
              :stroke-width="18"
              :text-inside="true"
            >
              <span class="progress-text">
                {{ statusMap[row.status] }} ({{ row.progress }}%)
              </span>
            </el-progress>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120">
          <template #default="{row}">
            <el-tag 
              :type="statusTagMap[row.status]"
              effect="dark"
            >
              {{ statusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button
              v-if="row.status === 'running'"
              type="danger"
              size="mini"
              @click="cancelTask(row.id)"
              icon="el-icon-close"
            >取消</el-button>
            <el-button
              v-if="row.status === 'error'"
              type="text"
              @click="showErrorDetails(row)"
              icon="el-icon-warning"
            >详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 解压对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="showDialog"
      width="500px"
      v-if="currentFile"
      :close-on-click-modal="false"
    >
      <div v-if="currentFile.is_volume" class="volume-tips">
        <el-alert type="info" :closable="false">
          <h4>分卷包解压须知：</h4>
          <ul>
            <li>请确认该分卷包包含全部 {{ currentFile.part_count }} 个分卷文件</li>
            <li>文件名必须符合分卷命名规范（如：filename.7z.001、filename.7z.002）</li>
            <li>请勿修改分卷包的文件名和扩展名</li>
          </ul>
        </el-alert>
      </div>

      <el-form label-width="80px">
        <el-form-item label="解压密码">
          <el-input
            v-model="password"
            type="password"
            placeholder="可选（如有密码请填写）"
            show-password
            clearable
          ></el-input>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="confirmExtract"
          :loading="extracting"
        >
          {{ extracting ? '解压中...' : '开始解压' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 错误详情对话框 -->
    <el-dialog
      title="解压错误详情"
      :visible.sync="errorDialogVisible"
      width="70%"
    >
      <div class="error-content">
        <h4 v-if="currentError.title" class="error-title">{{ currentError.title }}</h4>
        <pre class="error-log">{{ currentError.content }}</pre>
      </div>
    </el-dialog>

    <!-- 添加删除确认对话框 -->
  <el-dialog
    title="删除确认"
    :visible.sync="deleteDialogVisible"
    width="30%"
  >
    <span v-if="deleteTarget">
      确认删除 {{ deleteTarget.name }}（类型：{{ deleteTarget.type === 'file' ? '文件' : '目录' }}）？
    </span>
    <span slot="footer">
      <el-button @click="deleteDialogVisible = false">取消</el-button>
      <el-button
        type="danger"
        @click="confirmDeleteAction"
        :loading="deleting"
      >确定删除</el-button>
    </span>
  </el-dialog>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentPath: '/',
      deleteDialogVisible: false,
      deleting: false,
      deleteTarget: null,
      fileData: {
       files:{
        singleFiles: [],
        volumeGroups: []
       }
      },
      tasks: [],
      loading: false,
      showDialog: false,
      errorDialogVisible: false,
      extracting: false,
      password: '',
      currentFile: null,
      currentError: {
        title: '',
        content: ''
      },
      statusMap: {
        waiting: '等待中',
        running: '解压中',
        success: '已完成',
        error: '已失败'
      },
      statusTagMap: {
        waiting: 'info',
        running: 'warning',
        success: 'success',
        error: 'danger'
      },
      pollInterval: null
    }
  },
  computed: {
    pathParts() {
      return this.currentPath.split('/').filter(p => p)
    },
    dialogTitle() {
      if (!this.currentFile) return '解压选项'
      return this.currentFile.is_volume 
        ? `解压分卷包：${this.currentFile.base_name}`
        : `解压文件：${this.currentFile.name}`
    }
  },
  mounted() {
    this.loadFiles()
    this.startPolling()
  },
  beforeDestroy() {
    clearInterval(this.pollInterval)
  },
  methods: {
    confirmDelete(row) {
      this.deleteTarget = {
        path: `${this.currentPath}/${row.name}`.replace(/\/\//g, '/'),
        name: row.name,
        type: row.type
      }
      console.log(this.deleteTarget);
      
      this.deleteDialogVisible = true
    },
    async confirmDeleteAction() {
      this.deleting = true
      try {
        await this.$http.post('/api/delete', {
          path: this.deleteTarget.path,
          item_type: this.deleteTarget.type
        })
        this.$message.success('删除成功')
        this.loadFiles() // 刷新列表
      } catch (error) {
        this.$notify.error({
          title: '删除失败',
          message: error.response?.data?.error || '未知错误'
        })
      } finally {
        this.deleting = false
        this.deleteDialogVisible = false
      }
    },
    getBreadcrumbLink(index) {
      const parts = this.pathParts.slice(0, index + 1)
      return parts.length > 0 ? parts.join('/') : ''
    },
    enterDirectory(row) {
      this.currentPath = [this.currentPath, row.name].filter(p => p).join('/')
      this.loadFiles()
    },
    goUp() {
      const parts = this.currentPath.split('/')
      parts.pop()
      this.currentPath = parts.join('/')
      this.loadFiles()
    },
    async loadFiles() {
      this.loading = true
      try {
        const params = { path: this.currentPath }
        const res = await this.$http.get('/api/files', { params })
        this.fileData = res.data
        // 同步当前路径显示
        this.currentPath = res.data.currentPath || ''
      } catch (error) {
        this.showErrorNotification('加载目录失败', error)
      } finally {
        this.loading = false
      }
    },

    handleContextMenu(row, event) {
      event.preventDefault()
      this.startExtract(row)
    },
    startExtract(file) {
      this.currentFile = file.is_volume ? 
        { ...file, name: file.base_name, is_volume: true } : 
        { ...file, is_volume: false }
      this.showDialog = true
    },
    startExtractVolume(volumeGroup) {
      this.currentFile = {
        
        ...volumeGroup,
        name: volumeGroup.base_name,
        is_volume: true
      }
      this.showDialog = true
    },
    async confirmExtract() {
    
    
    
      this.extracting = true
      try {
        const payload = {
          filename: this.currentFile.name,
          password: this.password
        }
        console.log(this.currentFile);
        if (this.currentFile.is_volume) {
          payload.filename =   this.currentPath+'/'+this.currentFile.part_files[0]  // 分卷包需要传递第一个分卷的文件名
        }else{
          payload.filename =   this.currentPath+'/'+this.currentFile.name // 普通压缩包// 普通压缩包需要传递完整的文件名
        }
        
        const res = await this.$http.post('/api/extract', payload)
        
        this.$message.success({
          message: `解压任务已创建 (ID: ${res.data.task_id})`,
          duration: 3000,
          showClose: true
        })
        
        this.showDialog = false
        this.password = ''
      } catch (error) {
        this.showErrorNotification('解压启动失败', error)
      } finally {
        this.extracting = false
      }
    },
    startPolling() {
      this.pollInterval = setInterval(async () => {
        try {
          const res = await this.$http.get('/api/tasks')
          this.tasks = res.data.map(task => ({
            ...task,
            start_time: this.formatTime(task.start_time),
            logs: task.logs.slice(-5)  // 仅保留最近5条日志
          }))
          console.log(this.tasks);
          
        } catch (error) {
          console.error('任务轮询错误:', error)
        }
      }, 2000)
    },
    showErrorDetails(row) {
      this.currentError = {
        title: `解压失败：${row.filename}`,
        content: row.logs.join('\n')
      }
      this.errorDialogVisible = true
    },
    showErrorNotification(title, error) {
      const message = error.response?.data?.error || error.message || '未知错误'
      this.$notify.error({
        title,
        message,
        duration: 5000
      })
      console.error(`${title}:`, error)
    },
    formatTime(timestamp) {
      return new Date(timestamp * 1000).toLocaleString()
    },
    formatSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const units = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${units[i]}`
    },
    formatDate(timestamp) {
      return new Date(timestamp * 1000).toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getStatus(status) {
      const statusMap = {
        error: 'exception',
        success: 'success',
        default: ''
      }
      return statusMap[status] || ''
    },
    taskRowStyle({ row }) {
      return row.status === 'error' ? 'error-row' : ''
    },
    async cancelTask(taskId) {
      try {
        await this.$http.delete(`/api/tasks/${taskId}`)
        this.$message.success('取消请求已发送')
      } catch (error) {
        this.showErrorNotification('取消失败', error)
      }
    }
  }
}
</script>

<style scoped>
.delete-btn {
  color: #F56C6C;
}
.delete-btn:hover {
  color: #f78989;
}
.container {
  padding: 20px;
}

.file-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.task-card {
  margin-top: 24px;
}

.filename {
  display: inline-block;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
}

.volume-tips ul {
  padding-left: 20px;
  margin: 8px 0;
}

.volume-tips li {
  line-height: 1.8;
  font-size: 13px;
}

.error-content {
  background: #f8f8f8;
  border-radius: 4px;
  padding: 16px;
}

.error-title {
  color: #F56C6C;
  margin: 0 0 12px 0;
}

.error-log {
  white-space: pre-wrap;
  font-family: monospace;
  line-height: 1.6;
  margin: 0;
}

.progress-text {
  font-size: 12px;
  font-weight: bold;
}

::v-deep .volume-row {
  background-color: #f0f9ff;
}

::v-deep .error-row {
  background-color: #fef0f0;
}
.directory-nav {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
.directory-name {
  color: #606266;
  cursor: pointer;
}
.directory-name:hover {
  color: #409EFF;
  text-decoration: underline;
}
::v-deep .directory-row {
  cursor: pointer;
}
::v-deep .directory-row:hover td {
  background-color: #f0f9eb !important;
}
</style>
