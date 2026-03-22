<template>
  <div class="rag-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>RAG文档管理</span>
          <el-space>
            <el-button type="primary" @click="handleSync" :loading="syncing">
              <el-icon><Refresh /></el-icon>
              同步文档
            </el-button>
            <el-button @click="showPreviewDialog = true">
              <el-icon><View /></el-icon>
              预览切割
            </el-button>
          </el-space>
        </div>
      </template>

      <el-row :gutter="20" class="status-row">
        <el-col :span="8">
          <el-statistic title="待同步" :value="status.pendingCount">
            <template #suffix>
              <el-tag type="warning" size="small">篇</el-tag>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="已同步" :value="status.syncedCount">
            <template #suffix>
              <el-tag type="success" size="small">篇</el-tag>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="失败" :value="status.failedCount">
            <template #suffix>
              <el-tag type="danger" size="small">篇</el-tag>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="showPreviewDialog" title="预览切割效果" width="800px">
      <el-form :model="previewForm" label-width="100px">
        <el-form-item label="文档内容">
          <el-input
            v-model="previewForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入要预览切割的文档内容"
          />
        </el-form-item>
        <el-form-item label="块大小">
          <el-input-number v-model="previewForm.chunkSize" :min="100" :max="2000" :step="100" />
        </el-form-item>
        <el-form-item label="重叠大小">
          <el-input-number v-model="previewForm.chunkOverlap" :min="0" :max="200" :step="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPreviewDialog = false">取消</el-button>
        <el-button type="primary" @click="handlePreview" :loading="previewing">预览</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showResultDialog" title="切割结果" width="800px">
      <div v-for="(chunk, index) in previewResult.chunks" :key="index" class="chunk-item">
        <div class="chunk-header">
          <el-tag>块 {{ index + 1 }}</el-tag>
          <span class="chunk-length">{{ chunk.content.length }} 字符</span>
        </div>
        <div class="chunk-content">{{ chunk.content }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSyncStatus, triggerSync, previewSplit, type RagSyncStatus, type SplitPreviewResponse } from '@/api/rag'

const status = ref<RagSyncStatus>({
  pendingCount: 0,
  syncedCount: 0,
  failedCount: 0
})

const syncing = ref(false)
const previewing = ref(false)
const showPreviewDialog = ref(false)
const showResultDialog = ref(false)

const previewForm = ref({
  content: '',
  chunkSize: 500,
  chunkOverlap: 50
})

const previewResult = ref<SplitPreviewResponse>({
  status: '',
  chunks: [],
  chunkCount: 0,
  originalCount: 0
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
    console.error('Failed to sync:', error)
  } finally {
    syncing.value = false
  }
}

const handlePreview = async () => {
  if (!previewForm.value.content) {
    ElMessage.warning('请输入文档内容')
    return
  }

  previewing.value = true
  try {
    const res = await previewSplit({
      documents: [{ content: previewForm.value.content }],
      chunkSize: previewForm.value.chunkSize,
      chunkOverlap: previewForm.value.chunkOverlap
    })
    previewResult.value = res.data
    showPreviewDialog.value = false
    showResultDialog.value = true
  } catch (error) {
    console.error('Failed to preview:', error)
  } finally {
    previewing.value = false
  }
}

onMounted(() => {
  fetchStatus()
})
</script>

<style lang="scss" scoped>
.rag-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .status-row {
    padding: 20px 0;
  }

  .chunk-item {
    margin-bottom: 16px;
    padding: 12px;
    border: 1px solid #ebeef5;
    border-radius: 4px;

    .chunk-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .chunk-length {
        font-size: 12px;
        color: #909399;
      }
    }

    .chunk-content {
      font-size: 14px;
      color: #606266;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }
}
</style>
