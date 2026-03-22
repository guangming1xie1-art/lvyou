<template>
  <div class="user-management">
    <div class="page-header">
      <h1>用户管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>新建用户
      </el-button>
    </div>

    <el-card>
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="queryParams.keyword" placeholder="用户名/邮箱/姓名" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="全部" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="realName" label="真实姓名" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="isActive" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'danger'">
              {{ row.isActive ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
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

    <!-- 用户表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新建用户'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="form.realName" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { useUserStore } from '@/stores';
import { storeToRefs } from 'pinia';
import type { User, UserRequest } from '@/types';
import type { FormInstance, FormRules } from 'element-plus';

const userStore = useUserStore();
const { users, total, loading } = storeToRefs(userStore);

const queryParams = reactive({
  page: 0,
  size: 20,
  keyword: '',
  status: undefined as boolean | undefined
});

const dialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const formRef = ref<FormInstance>();

const form = reactive<UserRequest>({
  username: '',
  email: '',
  password: '',
  realName: '',
  phone: '',
  isActive: true,
  roleIds: []
});

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }]
};

let currentId: number | null = null;

onMounted(() => {
  loadData();
});

function loadData() {
  userStore.fetchUsers(queryParams);
}

function handleSearch() {
  queryParams.page = 0;
  loadData();
}

function handleReset() {
  queryParams.keyword = '';
  queryParams.status = undefined;
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
    username: '',
    email: '',
    password: '',
    realName: '',
    phone: '',
    isActive: true,
    roleIds: []
  });
  dialogVisible.value = true;
}

function handleEdit(row: User) {
  isEdit.value = true;
  currentId = row.id;
  Object.assign(form, {
    username: row.username,
    email: row.email,
    realName: row.realName || '',
    phone: row.phone || '',
    isActive: row.isActive,
    roleIds: []
  });
  dialogVisible.value = true;
}

async function handleSubmit() {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    
    submitting.value = true;
    try {
      if (isEdit.value && currentId) {
        await userStore.update(currentId, form);
        ElMessage.success('更新成功');
      } else {
        await userStore.create(form);
        ElMessage.success('创建成功');
      }
      dialogVisible.value = false;
      loadData();
    } catch (error) {
      // 错误已在请求拦截器中处理
    } finally {
      submitting.value = false;
    }
  });
}

async function handleDelete(row: User) {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      type: 'warning'
    });
    await userStore.remove(row.id);
    ElMessage.success('删除成功');
  } catch {
    // 用户取消
  }
}

function formatDate(date: string) {
  return new Date(date).toLocaleString();
}
</script>

<style scoped>
.user-management {
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
</style>
