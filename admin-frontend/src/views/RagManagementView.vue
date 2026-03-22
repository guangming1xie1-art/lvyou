<template>
  <div class="rag-management">
    <div class="page-header">
      <h1>RAG文档管理</h1>
      <div>
        <el-button type="success" @click="handleSync" :loading="syncing">
          <el-icon><Refresh /></el-icon>同步全部
        </el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>新建文档
        </el-button>
      </div>
    </div>

    <el-card>
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="全部" clearable>
            <el-option
              v-for="status in syncStatus"
              :key="status.value"
              :label="status.label"
              :value="status.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="实体类型">
          <el-select v-model="queryParams.entityType" placeholder="全部" clearable>
            <el-option
              v-for="type in entityTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="documents" v-loading="loading" style="width: 100%">
        <el-table-column prop="entityType" label="实体类型">
          <template #default="{ row }">
            {{ getEntityTypeLabel(row.entityType) }}
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" show-overflow-tooltip />
        <el-table-column prop="docType" label="文档类型">
          <template #default="{ row }">
            {{ getDocTypeLabel(row.docType) }}
          </template>
        </el-table-column>
        <el-table-column prop="chunkCount" label="分块数" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastSyncTime" label="最后同步">
          <template #default="{ row }">
            {{ row.lastSyncTime ? formatDate(row.lastSyncTime) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" size="small" @click="handlePreview(row)">预览</el-button>
            <el-button type="warning" size="small" @click="handleSyncSingle(row)">同步</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 文档表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑文档' : '新建文档'"
      width="700px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="实体类型" prop="entityType">
          <el-select v-model="form.entityType" style="width: 100%">
            <el-option
              v-for="type in entityTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="实体ID" prop="entityId">
          <el-input v-model="form.entityId" placeholder="UUID格式" />
        </el-form-item>
        <el-form-item label="来源" prop="source">
          <el-input v-model="form.source" placeholder="数据来源" />
        </el-form-item>
        <el-form-item label="文档类型" prop="docType">
          <el-select v-model="form.docType" style="width: 100%">
            <el-option
              v-for="type in docTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="输入文档内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="分块预览"
      width="800px"
    >
      <div v-if="previewLoading" class="preview-loading">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="splitPreview">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="原文档数">{{ splitPreview.originalCount }}</el-descriptions-item>
          <el-descriptions-item label="分块数">{{ splitPreview.chunkCount }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ splitPreview.status }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div class="preview-chunks">
          <div
            v-for="(chunk, index) in splitPreview.chunks"
            :key="index"
            class="chunk-item"
          >
            <div class="chunk-header">分块 {{ index + 1 }}</div>
            <div class="chunk-content">{{ chunk.content }}</div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Refresh } from '@element-plus/icons-vue';
import { useRagStore } from '@/stores';
import { storeToRefs } from 'pinia';
import type { RagDocument, RagDocumentRequest, RagQueryParams } from '@/types';
import type { FormInstance, FormRules } from 'element-plus';
import { ENTITY_TYPES, DOC_TYPES, SYNC_STATUS } from '@/types';

const ragStore = useRagStore();
const { documents, total, loading, splitPreview } = storeToRefs(ragStore);

const entityTypes = ENTITY_TYPES;
const docTypes = DOC_TYPES;
const syncStatus = SYNC_STATUS;

const queryParams = reactive<RagQueryParams>({
  page: 0,
  size: 20,
  status: '',
  entityType: ''
});

const dialogVisible = ref(false);
const previewDialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const syncing = ref(false);
const previewLoading = ref(false);
const formRef = ref<FormInstance>();

const form = reactive<RagDocumentRequest>({
  entityType: '',
  entityId: '',
  content: '',
  source: '',
  docType: 'default',
  metadata: {}
});

let currentId: string | null = null;

const rules: FormRules = {
  entityType: [{ required: true, message: '请选择实体类型', trigger: 'change' }],
  entityId: [{ required: true, message: '请输入实体ID', trigger: 'blur' }],
  source: [{ required: true, message: '请输入来源', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
};

onMounted(() => {
  loadData();
});

function loadData() {
  ragStore.fetchDocuments(queryParams);
}

function handleSearch() {
  queryParams.page = 0;
  loadData();
}

function handleReset() {
  queryParams.status = '';
  queryParams.entityType = '';
  queryParams.page = 0;
  loadData();
}

function handleSizeChange(size: number) {
  queryParams.size = size;
  loadData();
}

function handlePageChange(page: number) {
  queryParams.page = page - 1;
  loadData();
}

function handleCreate() {
  isEdit.value = false;
  currentId = null;
  Object.assign(form, {
    entityType: '',
    entityId: '',
    content: '',
    source: '',
    docType: 'default',
    metadata: {}
  });
  dialogVisible.value = true;
}

function handleEdit(row: RagDocument) {
  isEdit.value = true;
  currentId = row.id;
  Object.assign(form, {
    entityType: row.entityType,
    entityId: row.entityId,
    content: row.content,
    source: row.source,
    docType: row.docType,
    metadata: row.metadata
  });
  dialogVisible.value = true;
}

async function handlePreview(row: RagDocument) {
  previewDialogVisible.value = true;
  previewLoading.value = true;
  try {
    await ragStore.preview(row.content);
  } finally {
    previewLoading.value = false;
  }
}

async function handleSync() {
  syncing.value = true;
  try {
    await ragStore.sync();
    ElMessage.success('同步任务已启动');
    loadData();
  } finally {
    syncing.value = false;
  }
}

async function handleSyncSingle(row: RagDocument) {
  try {
    await ragStore.sync([row.id]);
    ElMessage.success('同步任务已启动');
    loadData();
  } catch {
    // 错误已处理
  }
}

async function handleSubmit() {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    
    submitting.value = true;
    try {
      if (isEdit.value && currentId) {
        await ragStore.update(currentId, form);
        ElMessage.success('更新成功');
      } else {
        await ragStore.create(form);
        ElMessage.success('创建成功');
      }
      dialogVisible.value = false;
      loadData();
    } finally {
      submitting.value = false;
    }
  });
}

async function handleDelete(row: RagDocument) {
  try {
    await ElMessageBox.confirm('确定要删除该文档吗？', '提示', {
      type: 'warning'
    });
    await ragStore.remove(row.id);
    ElMessage.success('删除成功');
  } catch {
    // 用户取消
  }
}

function getEntityTypeLabel(value: string) {
  return entityTypes.find(t => t.value === value)?.label || value;
}

function getDocTypeLabel(value: string) {
  return docTypes.find(t => t.value === value)?.label || value;
}

function getStatusLabel(value: string) {
  return syncStatus.find(s => s.value === value)?.label || value;
}

function getStatusType(value: string) {
  return syncStatus.find(s => s.value === value)?.color || 'info';
}

function formatDate(date: string) {
  return new Date(date).toLocaleString();
}
</script>

<style scoped>
.rag-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.preview-loading {
  padding: 20px;
}

.preview-chunks {
  max-height: 400px;
  overflow-y: auto;
}

.chunk-item {
  margin-bottom: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.chunk-header {
  background: #f5f7fa;
  padding: 8px 12px;
  font-weight: bold;
  border-bottom: 1px solid #e4e7ed;
}

.chunk-content {
  padding: 12px;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 150px;
  overflow-y: auto;
}
</style>
