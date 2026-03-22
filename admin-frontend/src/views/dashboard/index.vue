<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon size="32"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ status.pendingCount }}</div>
              <div class="stat-label">待同步</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon synced">
              <el-icon size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ status.syncedCount }}</div>
              <div class="stat-label">已同步</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon failed">
              <el-icon size="32"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ status.failedCount }}</div>
              <div class="stat-label">失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">总文档数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="action-card">
      <template #header>
        <span>快捷操作</span>
      </template>
      <el-space>
        <el-button type="primary" @click="handleSync" :loading="syncing">
          <el-icon><Refresh /></el-icon>
          触发同步
        </el-button>
        <el-button @click="handleRetry" :loading="retrying">
          <el-icon><RefreshRight /></el-icon>
          重试失败
        </el-button>
      </el-space>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSyncStatus, triggerSync, retryFailed, type RagSyncStatus } from '@/api/rag'

const status = ref<RagSyncStatus>({
  pendingCount: 0,
  syncedCount: 0,
  failedCount: 0
})

const syncing = ref(false)
const retrying = ref(false)

const totalCount = computed(() => {
  return status.value.pendingCount + status.value.syncedCount + status.value.failedCount
})

const fetchStatus = async () => {
  try {
    const res = await getSyncStatus()
    status.value = res.data
  } catch (error) {
    console.error('Failed to fetch status:', error)
  }
}

const handleSync = async () => {
  syncing.value = true
  try {
    await triggerSync()
    ElMessage.success('同步任务已触发')
    setTimeout(fetchStatus, 2000)
  } catch (error) {
    console.error('Failed to trigger sync:', error)
  } finally {
    syncing.value = false
  }
}

const handleRetry = async () => {
  retrying.value = true
  try {
    await retryFailed()
    ElMessage.success('重试任务已触发')
    setTimeout(fetchStatus, 2000)
  } catch (error) {
    console.error('Failed to retry:', error)
  } finally {
    retrying.value = false
  }
}

onMounted(() => {
  fetchStatus()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      
      .stat-icon {
        width: 64px;
        height: 64px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        
        &.pending {
          background-color: #e6a23c;
          color: #fff;
        }
        
        &.synced {
          background-color: #67c23a;
          color: #fff;
        }
        
        &.failed {
          background-color: #f56c6c;
          color: #fff;
        }
        
        &.total {
          background-color: #409eff;
          color: #fff;
        }
      }
      
      .stat-info {
        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #303133;
        }
        
        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }
  
  .action-card {
    margin-top: 20px;
  }
}
</style>
