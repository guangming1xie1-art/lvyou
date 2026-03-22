<template>
  <div class="dashboard">
    <h1>仪表盘</h1>
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats?.userCount || 0 }}</div>
          <div class="stat-label">用户总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats?.documentCount || 0 }}</div>
          <div class="stat-label">文档总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats?.syncedCount || 0 }}</div>
          <div class="stat-label">已同步</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats?.pendingCount || 0 }}</div>
          <div class="stat-label">待同步</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card warning">
          <div class="stat-value">{{ stats?.failedCount || 0 }}</div>
          <div class="stat-label">同步失败</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card success">
          <div class="stat-value">{{ stats?.todayActiveUsers || 0 }}</div>
          <div class="stat-label">今日活跃用户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card info">
          <div class="stat-value">{{ stats?.todayApiCalls || 0 }}</div>
          <div class="stat-label">今日API调用</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="service-status">
      <template #header>
        <span>服务状态</span>
      </template>
      <el-table :data="stats?.services || []" style="width: 100%">
        <el-table-column prop="name" label="服务名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'UP' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="instances" label="实例数" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRagStore } from '@/stores';
import { storeToRefs } from 'pinia';

const ragStore = useRagStore();
const { dashboardStats: stats } = storeToRefs(ragStore);

onMounted(() => {
  ragStore.fetchDashboardStats();
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
}

.stat-card .stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.stat-card .stat-label {
  font-size: 14px;
  color: #666;
}

.stat-card.warning .stat-value {
  color: #e6a23c;
}

.stat-card.success .stat-value {
  color: #67c23a;
}

.stat-card.info .stat-value {
  color: #909399;
}

.service-status {
  margin-top: 20px;
}
</style>
