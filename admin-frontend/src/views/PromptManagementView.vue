<template>
  <div class="prompt-management">
    <div class="page-header">
      <h1>提示词管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>新建提示词
      </el-button>
    </div>

    <el-card>
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="分类">
          <el-select v-model="queryParams.category" placeholder="全部" clearable>
            <el-option
              v-for="cat in categories"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="prompts" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="category" label="分类">
          <template #default="{ row }">
            {{ getCategoryLabel(row.category) }}
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="isActive" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'info'">
              {{ row.isActive ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间">
          <template #default="{ row }">
            {{ formatDate(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" size="small" @click="handleTest(row)">测试</el-button>
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

    <!-- 提示词表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑提示词' : '新建提示词'"
      width="700px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="输入提示词内容，使用 {{variable}} 表示变量"
          />
        </el-form-item>
        <el-form-item label="变量">
          <el-tag
            v-for="(varName, index) in form.variables"
            :key="index"
            closable
            @close="removeVariable(index)"
            style="margin-right: 10px; margin-bottom: 5px"
          >
            {{ varName }}
          </el-tag>
          <el-input
            v-if="inputVisible"
            ref="inputRef"
            v-model="inputValue"
            size="small"
            style="width: 100px"
            @keyup.enter="addVariable"
            @blur="addVariable"
          />
          <el-button v-else size="small" @click="showInput">+ 添加变量</el-button>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="form.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.isActive" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 测试对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试提示词"
      width="700px"
    >
      <el-form label-width="100px">
        <el-form-item
          v-for="varName in currentPrompt?.variables"
          :key="varName"
          :label="varName"
        >
          <el-input v-model="testVariables[varName]" />
        </el-form-item>
      </el-form>
      <el-divider />
      <div v-if="testResult">
        <h4>渲染结果：</h4>
        <pre class="test-result">{{ testResult.renderedPrompt }}</pre>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="runTest" :loading="testing">运行测试</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { usePromptStore } from '@/stores';
import { storeToRefs } from 'pinia';
import type { Prompt, PromptRequest } from '@/types';
import type { FormInstance, FormRules } from 'element-plus';
import { PROMPT_CATEGORIES } from '@/types';

const promptStore = usePromptStore();
const { prompts, total, loading } = storeToRefs(promptStore);

const categories = PROMPT_CATEGORIES;

const queryParams = reactive({
  page: 0,
  size: 20,
  category: ''
});

const dialogVisible = ref(false);
const testDialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const testing = ref(false);
const formRef = ref<FormInstance>();
const inputRef = ref<HTMLInputElement>();

const form = reactive<PromptRequest>({
  name: '',
  category: '',
  content: '',
  variables: [],
  description: '',
  version: '1.0.0',
  isActive: true
});

const inputVisible = ref(false);
const inputValue = ref('');

const testVariables = reactive<Record<string, string>>({});
const testResult = ref<any>(null);

let currentId: string | null = null;
let currentPrompt = ref<Prompt | null>(null);

const rules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
};

onMounted(() => {
  loadData();
});

function loadData() {
  promptStore.fetchPrompts(queryParams);
}

function handleSearch() {
  queryParams.page = 0;
  loadData();
}

function handleReset() {
  queryParams.category = '';
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
    name: '',
    category: '',
    content: '',
    variables: [],
    description: '',
    version: '1.0.0',
    isActive: true
  });
  dialogVisible.value = true;
}

function handleEdit(row: Prompt) {
  isEdit.value = true;
  currentId = row.id;
  Object.assign(form, {
    name: row.name,
    category: row.category,
    content: row.content,
    variables: [...row.variables],
    description: row.description || '',
    version: row.version,
    isActive: row.isActive
  });
  dialogVisible.value = true;
}

function handleTest(row: Prompt) {
  currentPrompt.value = row;
  currentId = row.id;
  // 初始化测试变量
  Object.keys(testVariables).forEach(key => delete testVariables[key]);
  row.variables.forEach(v => {
    testVariables[v] = '';
  });
  testResult.value = null;
  testDialogVisible.value = true;
}

async function runTest() {
  if (!currentId) return;
  testing.value = true;
  try {
    testResult.value = await promptStore.test(currentId, testVariables);
  } finally {
    testing.value = false;
  }
}

async function handleSubmit() {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    
    submitting.value = true;
    try {
      if (isEdit.value && currentId) {
        await promptStore.update(currentId, form);
        ElMessage.success('更新成功');
      } else {
        await promptStore.create(form);
        ElMessage.success('创建成功');
      }
      dialogVisible.value = false;
      loadData();
    } finally {
      submitting.value = false;
    }
  });
}

async function handleDelete(row: Prompt) {
  try {
    await ElMessageBox.confirm('确定要删除该提示词吗？', '提示', {
      type: 'warning'
    });
    await promptStore.remove(row.id);
    ElMessage.success('删除成功');
  } catch {
    // 用户取消
  }
}

function showInput() {
  inputVisible.value = true;
  nextTick(() => {
    inputRef.value?.focus();
  });
}

function addVariable() {
  if (inputValue.value) {
    if (!form.variables) {
      form.variables = [];
    }
    form.variables.push(inputValue.value);
  }
  inputVisible.value = false;
  inputValue.value = '';
}

function removeVariable(index: number) {
  form.variables?.splice(index, 1);
}

function getCategoryLabel(value: string) {
  return categories.find(c => c.value === value)?.label || value;
}

function formatDate(date: string) {
  return new Date(date).toLocaleString();
}
</script>

<style scoped>
.prompt-management {
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

.test-result {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
