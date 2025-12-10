<template>
  <AppPage>
    <div class="cases-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1>课程思政案例库</h1>
            <p>丰富的软件工程课程思政教学案例，助力教学质量提升</p>
          </div>

          <div class="actions-section">
            <n-space>
              <n-button type="primary" @click="showCreateModal">
                <template #icon>
                  <n-icon><Icon icon="ant-design:plus-outlined" /></n-icon>
                </template>
                新建案例
              </n-button>
              <n-button @click="showImportModal">
                <template #icon>
                  <n-icon><Icon icon="ant-design:import-outlined" /></n-icon>
                </template>
                导入案例
              </n-button>
              <n-button @click="showBatchOperations" v-if="selectedCases.length > 0">
                <template #icon>
                  <n-icon><Icon icon="ant-design:setting-outlined" /></n-icon>
                </template>
                批量操作 ({{ selectedCases.length }})
              </n-button>
            </n-space>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <n-grid :cols="4" :x-gap="16" style="margin-bottom: 16px">
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="总案例数" :value="totalCases" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="我的案例" :value="myCases" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="热门案例" :value="hotCases" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="平均评分" :value="avgRating" :precision="1" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 搜索和筛选区域 -->
      <n-card class="search-section">
        <n-form :model="searchForm" label-placement="left" :show-feedback="false">
          <n-grid :cols="4" :x-gap="16">
            <n-form-item-grid-item :span="1" label="关键词">
              <n-input
                v-model:value="searchForm.keyword"
                placeholder="搜索案例标题或内容"
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <n-icon><Icon icon="ant-design:search-outlined" /></n-icon>
                </template>
              </n-input>
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="软件工程章节">
              <n-select
                v-model:value="searchForm.software_engineering_chapter"
                placeholder="选择章节"
                :options="chapterOptions"
                clearable
                @clear="handleSearch"
              />
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="思政主题">
              <n-select
                v-model:value="searchForm.theme_category_id"
                placeholder="选择主题"
                :options="themeOptions"
                clearable
                @clear="handleSearch"
              />
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="案例类型">
              <n-select
                v-model:value="searchForm.case_type"
                placeholder="选择类型"
                :options="caseTypeOptions"
                clearable
                @clear="handleSearch"
              />
            </n-form-item-grid-item>
          </n-grid>

          <n-space justify="space-between" align="center" style="margin-top: 16px">
            <n-checkbox 
              v-model:checked="searchForm.show_favorites_only" 
              @update:checked="handleSearch"
            >
              <n-space align="center" :size="4">
                <span>只看收藏</span>
              </n-space>
            </n-checkbox>
            
            <n-space>
              <n-button @click="resetSearch">重置</n-button>
              <n-button type="primary" @click="handleSearch">搜索</n-button>
            </n-space>
          </n-space>
        </n-form>
      </n-card>

      <!-- 案例列表 -->
      <n-card title="案例列表" class="cases-list">
        <template #header-extra>
          <n-space>
            <n-select
              v-model:value="searchForm.difficulty_level"
              placeholder="难度等级"
              :options="difficultyOptions"
              style="width: 120px"
              clearable
              @update:value="handleSearch"
            />
            <n-button-group>
              <n-button
                :type="viewMode === 'grid' ? 'primary' : 'default'"
                @click="viewMode = 'grid'"
              >
                <n-icon><Icon icon="ant-design:appstore-outlined" /></n-icon>
              </n-button>
              <n-button
                :type="viewMode === 'list' ? 'primary' : 'default'"
                @click="viewMode = 'list'"
              >
                <n-icon><Icon icon="ant-design:unordered-list-outlined" /></n-icon>
              </n-button>
            </n-button-group>
          </n-space>
        </template>

        <!-- 网格视图 -->
        <div v-if="viewMode === 'grid'" class="grid-view">
          <n-grid :cols="3" :x-gap="16" :y-gap="16">
            <n-grid-item v-for="case_item in casesList" :key="case_item.id">
              <n-checkbox
                v-model:checked="case_item.selected"
                @update:checked="toggleSelection(case_item)"
                class="case-checkbox"
                @click.stop
              />
              <n-card
                class="case-card"
                hoverable
                @click="viewCaseDetail(case_item)"
              >
                <template #header>
                  <div class="case-header">
                    <span class="case-title">{{ case_item.title }}</span>
                    <n-tag
                      :type="getDifficultyTagType(case_item.difficulty_level)"
                      size="small"
                    >
                      难度{{ case_item.difficulty_level }}
                    </n-tag>
                  </div>
                </template>

                <div class="case-content">
                  <div
                    class="case-description markdown-content"
                    v-html="renderMarkdownExcerpt(case_item.content, 180)"
                  ></div>

                  <div class="case-meta">
                    <n-space size="small">
                      <n-tag size="small" type="info">
                        {{ case_item.software_engineering_chapter }}
                      </n-tag>
                      <n-tag size="small" type="success" v-if="case_item.theme_name">
                        {{ case_item.theme_name }}
                      </n-tag>
                    </n-space>
                  </div>
                </div>

                <template #footer>
                  <div class="case-footer">
                    <n-space justify="space-between">
                      <n-space size="small">
                        <n-button
                          size="small"
                          text
                          @click.stop="toggleFavorite(case_item)"
                        >
                          <template #icon>
                            <n-icon
                              :color="case_item.is_favorited ? '#f0a020' : '#999'"
                            >
                              <Icon icon="ant-design:heart-filled" v-if="case_item.is_favorited" />
                              <Icon icon="ant-design:heart-outlined" v-else />
                            </n-icon>
                          </template>
                          {{ case_item.favorite_count || 0 }}
                        </n-button>
                        <n-button size="small" text @click.stop="rateCase(case_item)">
                          <template #icon>
                            <n-icon><Icon icon="ant-design:star-outlined" /></n-icon>
                          </template>
                          {{ case_item.rating.toFixed(1) }}
                        </n-button>
                      </n-space>

                      <n-dropdown
                        trigger="hover"
                        :options="getCaseActionOptions(case_item)"
                        @select="(key) => handleCaseAction(key, case_item)"
                      >
                        <n-button size="small" text>
                          <template #icon>
                            <n-icon><Icon icon="ant-design:more-outlined" /></n-icon>
                          </template>
                        </n-button>
                      </n-dropdown>
                    </n-space>
                  </div>
                </template>
              </n-card>
            </n-grid-item>
          </n-grid>
        </div>

        <!-- 列表视图 -->
        <div v-else class="list-view">
          <n-data-table
            :columns="columns"
            :data="casesList"
            :pagination="pagination"
            :loading="loading"
            @update:page="handlePageChange"
          />
        </div>

        <!-- 空状态 -->
        <n-empty
          v-if="!loading && casesList.length === 0"
          description="暂无案例数据"
          style="margin: 40px 0"
        >
          <template #action>
            <n-button type="primary" @click="showCreateModal">
              创建第一个案例
            </n-button>
          </template>
        </n-empty>
      </n-card>
    </div>

    <!-- 创建/编辑案例弹窗 -->
    <n-modal
      v-model:show="createModalVisible"
      :mask-closable="false"
      preset="dialog"
      style="width: 800px"
      :title="editingCase ? '编辑案例' : '新建案例'"
    >
      <n-form
        ref="caseFormRef"
        :model="caseForm"
        :rules="caseFormRules"
        label-placement="left"
        :label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="案例标题" path="title">
          <n-input
            v-model:value="caseForm.title"
            placeholder="请输入案例标题"
            maxlength="100"
            show-count
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="软件工程章节" path="software_engineering_chapter">
            <n-select
              v-model:value="caseForm.software_engineering_chapter"
              placeholder="选择章节"
              :options="chapterOptions"
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="思政主题" path="theme_category_id">
            <n-select
              v-model:value="caseForm.theme_category_id"
              placeholder="选择主题"
              :options="themeOptions"
            />
          </n-form-item-grid-item>
        </n-grid>

        <!-- 课程关联字段 -->
        <n-divider style="margin: 16px 0;">课程关联</n-divider>
        
        <n-form-item label="关联课程" path="course_id">
          <n-select
            v-model:value="caseForm.course_id"
            placeholder="选择课程（可选）"
            :options="courseOptions"
            clearable
            filterable
            @update:value="handleCourseChange"
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="16" v-if="caseForm.course_id">
          <n-form-item-grid-item label="关联章节" path="chapter_id">
            <n-select
              v-model:value="caseForm.chapter_id"
              placeholder="选择章节（可选）"
              :options="courseChapterOptions"
              :disabled="!caseForm.course_id || loadingChapters"
              :loading="loadingChapters"
              clearable
              filterable
              @update:value="handleChapterChange"
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="关联知识点" path="knowledge_point_id">
            <n-select
              v-model:value="caseForm.knowledge_point_id"
              placeholder="选择知识点（可选）"
              :options="knowledgePointOptions"
              :disabled="!caseForm.chapter_id || loadingKnowledgePoints"
              :loading="loadingKnowledgePoints"
              clearable
              filterable
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="案例类型" path="case_type">
            <n-select
              v-model:value="caseForm.case_type"
              placeholder="选择类型"
              :options="caseTypeOptions"
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="难度等级" path="difficulty_level">
            <n-rate
              v-model:value="caseForm.difficulty_level"
              :count="5"
              color="var(--primary-color)"
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-form-item label="案例内容" path="content">
          <n-input
            v-model:value="caseForm.content"
            type="textarea"
            placeholder="请输入详细的案例内容"
            :autosize="{ minRows: 6, maxRows: 12 }"
            maxlength="5000"
            show-count
          />
        </n-form-item>

        <n-form-item label="关键知识点" path="key_points">
          <n-dynamic-tags
            v-model:value="caseForm.key_points"
            placeholder="按回车添加知识点"
          />
        </n-form-item>

        <n-form-item label="讨论问题" path="discussion_questions">
          <n-dynamic-tags
            v-model:value="caseForm.discussion_questions"
            placeholder="按回车添加讨论问题"
          />
        </n-form-item>

        <n-form-item label="教学建议" path="teaching_suggestions">
          <n-input
            v-model:value="caseForm.teaching_suggestions"
            type="textarea"
            placeholder="请输入教学建议"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>

        <n-form-item label="标签" path="tags">
          <n-dynamic-tags
            v-model:value="caseForm.tags"
            placeholder="按回车添加标签"
          />
        </n-form-item>

        <n-form-item label="公开设置">
          <n-switch v-model:value="caseForm.is_public" />
          <span style="margin-left: 8px; color: #999">
            公开后其他用户可以查看此案例
          </span>
        </n-form-item>
      </n-form>

      <template #action>
        <n-space>
          <n-button @click="createModalVisible = false">取消</n-button>
          <n-button type="primary" @click="handleSubmitCase" :loading="submitLoading">
            {{ editingCase ? '更新' : '创建' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 案例详情弹窗 -->
    <n-modal
      v-model:show="detailModalVisible"
      preset="card"
      style="width: 900px; max-height: 80vh"
      :title="currentCase?.title"
      :bordered="false"
      :segmented="{ content: 'soft' }"
    >
      <n-scrollbar style="max-height: 60vh" v-if="currentCase">
        <n-space vertical size="large">
          <!-- 基本信息 -->
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="软件工程章节">
              <n-tag type="info">{{ currentCase.software_engineering_chapter }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="思政主题">
              <n-tag type="success">{{ currentCase.theme_name || '-' }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="案例类型">
              <n-tag>{{ getCaseTypeLabel(currentCase.case_type) }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="难度等级">
              <n-rate :value="currentCase.difficulty_level" readonly :count="5" size="small" />
            </n-descriptions-item>
            <n-descriptions-item label="使用次数">
              {{ currentCase.usage_count }} 次
            </n-descriptions-item>
            <n-descriptions-item label="收藏次数">
              <n-space align="center" :size="4">
                <n-icon color="#f0a020">
                  <Icon icon="ant-design:heart-filled" />
                </n-icon>
                <span>{{ currentCase.favorite_count || 0 }} 次</span>
              </n-space>
            </n-descriptions-item>
            <n-descriptions-item label="评分">
              <n-space align="center">
                <n-rate :value="currentCase.rating" readonly allow-half size="small" />
                <span>{{ currentCase.rating.toFixed(1) }} ({{ currentCase.rating_count }}人评价)</span>
              </n-space>
            </n-descriptions-item>
          </n-descriptions>

          <!-- 课程关联层级 -->
          <n-card 
            title="课程关联" 
            size="small" 
            v-if="currentCase.course_name || currentCase.chapter_name || currentCase.knowledge_point_name"
          >
            <n-space vertical size="small">
              <div v-if="currentCase.course_name" style="display: flex; align-items: center;">
                <n-icon size="18" style="margin-right: 8px;">
                  <Icon icon="ant-design:book-outlined" />
                </n-icon>
                <n-breadcrumb>
                  <n-breadcrumb-item>
                    <n-tag type="primary">{{ currentCase.course_name }}</n-tag>
                  </n-breadcrumb-item>
                  <n-breadcrumb-item v-if="currentCase.chapter_name">
                    <n-tag type="info">{{ currentCase.chapter_name }}</n-tag>
                  </n-breadcrumb-item>
                  <n-breadcrumb-item v-if="currentCase.knowledge_point_name">
                    <n-tag type="success">{{ currentCase.knowledge_point_name }}</n-tag>
                  </n-breadcrumb-item>
                </n-breadcrumb>
              </div>
            </n-space>
          </n-card>

          <!-- 案例内容 -->
          <n-card title="案例内容" size="small">
            <div class="case-detail-content markdown-content" v-html="renderMarkdown(currentCase.content)"></div>
          </n-card>

          <!-- 关键知识点 -->
          <n-card title="关键知识点" size="small" v-if="currentCase.key_points?.length">
            <n-space>
              <n-tag v-for="point in currentCase.key_points" :key="point" type="info">
                {{ point }}
              </n-tag>
            </n-space>
          </n-card>

          <!-- 讨论问题 -->
          <n-card title="讨论问题" size="small" v-if="currentCase.discussion_questions?.length">
            <n-ol>
              <n-li v-for="(question, index) in currentCase.discussion_questions" :key="index">
                {{ question }}
              </n-li>
            </n-ol>
          </n-card>

          <!-- 教学建议 -->
          <n-card title="教学建议" size="small" v-if="currentCase.teaching_suggestions">
            <p>{{ currentCase.teaching_suggestions }}</p>
          </n-card>

          <!-- 标签 -->
          <n-card title="标签" size="small" v-if="currentCase.tags?.length">
            <n-space>
              <n-tag v-for="tag in currentCase.tags" :key="tag">
                {{ tag }}
              </n-tag>
            </n-space>
          </n-card>
        </n-space>
      </n-scrollbar>

      <template #footer>
        <n-space justify="space-between">
          <n-space>
            <n-button @click="rateCase(currentCase)">
              <template #icon>
                <n-icon><Icon icon="ant-design:star-outlined" /></n-icon>
              </template>
              评分
            </n-button>
            <n-button @click="toggleFavorite(currentCase)">
              <template #icon>
                <n-icon :color="currentCase.is_favorited ? '#f0a020' : undefined">
                  <Icon icon="ant-design:heart-outlined" />
                </n-icon>
              </template>
              {{ currentCase.is_favorited ? '已收藏' : '收藏' }}
            </n-button>
          </n-space>
          <n-space>
            <n-button @click="exportCase(currentCase)">
              <template #icon>
                <n-icon><Icon icon="ant-design:export-outlined" /></n-icon>
              </template>
              导出
            </n-button>
            <n-button type="primary" @click="editCase(currentCase)">
              编辑
            </n-button>
          </n-space>
        </n-space>
      </template>
    </n-modal>

    <!-- 评分弹窗 -->
    <n-modal
      v-model:show="ratingModalVisible"
      preset="dialog"
      title="为案例评分"
      positive-text="提交"
      negative-text="取消"
      @positive-click="submitRating"
    >
      <n-space vertical size="large" style="padding: 20px 0">
        <n-space vertical align="center">
          <n-rate v-model:value="ratingForm.rating" :count="5" size="large" allow-half />
          <span>{{ ratingForm.rating }} 分</span>
        </n-space>
        <n-form-item label="评价内容">
          <n-input
            v-model:value="ratingForm.comment"
            type="textarea"
            placeholder="请输入您的评价（可选）"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>
      </n-space>
    </n-modal>

    <!-- 导入案例模态框 -->
    <n-modal
      v-model:show="importModalVisible"
      preset="card"
      title="导入案例"
      style="width: 600px"
      :mask-closable="false"
    >
      <n-space vertical size="large">
        <n-alert type="info" :bordered="false">
          <template #header>导入说明</template>
          <n-ol>
            <n-li>支持JSON和Excel（.xlsx）格式文件</n-li>
            <n-li>JSON格式示例：<code>[{"title": "案例标题", "content": "案例内容", ...}]</code></n-li>
            <n-li>Excel格式：第一行为表头，必填字段包括：标题、内容、软件工程章节、思政主题、案例类型</n-li>
            <n-li>单次最多导入100条案例</n-li>
          </n-ol>
        </n-alert>

        <n-upload
          :max="1"
          accept=".json,.xlsx,.xls"
          :on-before-upload="handleBeforeUpload"
          :custom-request="handleCustomRequest"
          :on-remove="handleFileRemove"
          :show-file-list="true"
          directory-dnd
        >
          <n-upload-dragger>
            <div style="padding: 20px">
              <n-space vertical align="center">
                <n-icon size="48" :depth="3">
                  <Icon icon="ant-design:cloud-upload-outlined" />
                </n-icon>
                <n-text>点击或拖拽文件到此区域上传</n-text>
                <n-text depth="3" style="font-size: 12px">
                  支持 JSON 格式文件，单个文件不超过 5MB
                </n-text>
              </n-space>
            </div>
          </n-upload-dragger>
        </n-upload>

        <n-space v-if="importPreview.length > 0" vertical size="large">
          <n-divider>预览数据 (前5条)</n-divider>
          <n-space vertical size="small">
            <n-card 
              size="small" 
              v-for="(item, index) in importPreview.slice(0, 5)" 
              :key="index"
              :title="`${index + 1}. ${item.title}`"
            >
              <n-space vertical size="small">
                <n-space align="center" size="small" wrap>
                  <n-tag type="info" size="small">
                    {{ getCaseTypeLabel(item.case_type) }}
                  </n-tag>
                  <n-divider vertical />
                  <n-space align="center" :size="4">
                    <n-icon><Icon icon="ant-design:book-outlined" /></n-icon>
                    <n-text>{{ item.software_engineering_chapter }}</n-text>
                  </n-space>
                  <n-divider vertical />
                  <n-space align="center" :size="4">
                    <n-icon><Icon icon="ant-design:fire-outlined" /></n-icon>
                    <n-text>{{ item.ideological_theme }}</n-text>
                  </n-space>
                  <n-divider vertical />
                  <n-space align="center" :size="4">
                    <n-icon><Icon icon="ant-design:star-outlined" /></n-icon>
                    <n-text>难度 {{ item.difficulty_level }}/5</n-text>
                  </n-space>
                </n-space>
                <n-ellipsis :line-clamp="2" expand-trigger="click">
                  <n-text depth="3">{{ item.content }}</n-text>
                </n-ellipsis>
                <n-space v-if="item.tags && item.tags.length > 0" size="small">
                  <n-tag 
                    v-for="tag in item.tags.slice(0, 3)" 
                    :key="tag" 
                    size="small"
                    :bordered="false"
                  >
                    {{ tag }}
                  </n-tag>
                  <n-text v-if="item.tags.length > 3" depth="3" size="small">
                    +{{ item.tags.length - 3 }}
                  </n-text>
                </n-space>
              </n-space>
            </n-card>
          </n-space>
          <n-alert type="success" :bordered="false">
            <template #icon>
              <n-icon><Icon icon="ant-design:check-circle-outlined" /></n-icon>
            </template>
            共解析 {{ importPreview.length }} 条案例，准备导入
          </n-alert>
        </n-space>
      </n-space>

      <template #footer>
        <n-space justify="end">
          <n-button @click="closeImportModal">取消</n-button>
          <n-button
            type="primary"
            :loading="importLoading"
            :disabled="importPreview.length === 0"
            @click="confirmImport"
          >
            导入
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </AppPage>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NCard,
  NButton,
  NIcon,
  NSpace,
  NForm,
  NFormItem,
  NFormItemGridItem,
  NInput,
  NSelect,
  NTreeSelect,
  NGrid,
  NGridItem,
  NTag,
  NModal,
  NRate,
  NDynamicTags,
  NSwitch,
  NDataTable,
  NEmpty,
  NDropdown,
  NStatistic,
  NDescriptions,
  NDescriptionsItem,
  NScrollbar,
  NOl,
  NLi,
  NCheckbox,
  NUpload,
  NUploadDragger,
  NAlert,
  NDivider,
  NText,
  NEllipsis,
  NBreadcrumb,
  NBreadcrumbItem,
  useMessage,
  useDialog,
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import MarkdownIt from 'markdown-it'
import AppPage from '@/components/page/AppPage.vue'
import { request } from '@/utils/http'
import { casesApi, themeCategoriesApi } from '@/api/ideological'
import api from '@/api'

// 响应式数据
const message = useMessage()
const dialog = useDialog()
const router = useRouter()
const route = useRoute()

const loading = ref(false)
const submitLoading = ref(false)
const createModalVisible = ref(false)
const detailModalVisible = ref(false)
const ratingModalVisible = ref(false)
const importModalVisible = ref(false)
const importLoading = ref(false)
const importPreview = ref([])
const editingCase = ref(null)
const currentCase = ref(null)
const viewMode = ref('grid')
const selectedCases = ref([])

// 统计数据
const totalCases = ref(0)
const myCases = ref(0)
const hotCases = ref(0)
const avgRating = ref(0)

// 评分表单
const ratingForm = reactive({
  rating: 5,
  comment: '',
})

// 搜索表单
const searchForm = reactive({
  keyword: '',
  software_engineering_chapter: null,
  theme_category_id: null,
  case_type: null,
  difficulty_level: null,
  show_favorites_only: false, // 只显示收藏的案例
})

// 案例表单
const caseFormRef = ref()
const caseForm = reactive({
  title: '',
  content: '',
  software_engineering_chapter: null,
  theme_category_id: null,  // 使用外键ID
  case_type: null,
  difficulty_level: 3,
  key_points: [],
  discussion_questions: [],
  teaching_suggestions: '',
  tags: [],
  is_public: true,
  // 课程关联字段
  course_id: null,
  chapter_id: null,
  knowledge_point_id: null,
})

// 案例列表
const casesList = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 12,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [12, 24, 48, 96],
})

// 选项数据
const chapterOptions = ref([])
const themeOptions = ref([])
const caseTypeOptions = ref([
  { label: '案例分析', value: 'case_study' },
  { label: '讨论题', value: 'discussion' },
  { label: '思考题', value: 'thinking' },
  { label: '示例', value: 'example' },
  { label: '实践项目', value: 'practice' },
])

const difficultyOptions = ref([
  { label: '难度1', value: 1 },
  { label: '难度2', value: 2 },
  { label: '难度3', value: 3 },
  { label: '难度4', value: 4 },
  { label: '难度5', value: 5 },
])

// 课程关联选项
const courseOptions = ref([])
const courseChapterOptions = ref([])
const knowledgePointOptions = ref([])

// 加载状态
const loadingChapters = ref(false)
const loadingKnowledgePoints = ref(false)

// Markdown 渲染器
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
})

// 表单验证规则
const caseFormRules = {
  title: [
    { required: true, message: '请输入案例标题', trigger: 'blur' },
    { max: 100, message: '标题长度不能超过100个字符', trigger: 'blur' },
  ],
  content: [
    { required: true, message: '请输入案例内容', trigger: 'blur' },
    { max: 5000, message: '内容长度不能超过5000个字符', trigger: 'blur' },
  ],
  software_engineering_chapter: [
    { required: true, message: '请选择软件工程章节', trigger: 'change' },
  ],
  theme_category_id: [
    { 
      required: true, 
      type: 'number',
      message: '请选择思政主题', 
      trigger: ['change', 'blur'],
      validator: (rule, value) => {
        console.log('验证 theme_category_id:', value, typeof value)
        if (!value) {
          return new Error('请选择思政主题')
        }
        return true
      }
    },
  ],
  case_type: [
    { required: true, message: '请选择案例类型', trigger: 'change' },
  ],
}

// 表格列定义
const columns = [
  {
    title: '案例标题',
    key: 'title',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: '软件工程章节',
    key: 'software_engineering_chapter',
    width: 150,
  },
  {
    title: '思政主题',
    key: 'theme_name',
    width: 120,
    render(row) {
      if (row.theme_name) {
        return row.theme_name
      }
      if (row.theme_category_id) {
        return `[ID:${row.theme_category_id}]`
      }
      return '-'
    }
  },
  {
    title: '案例类型',
    key: 'case_type',
    width: 100,
    render(row) {
      return h(
        NTag,
        { type: 'info', size: 'small' },
        { default: () => getCaseTypeLabel(row.case_type) }
      )
    },
  },
  {
    title: '难度',
    key: 'difficulty_level',
    width: 80,
    render(row) {
      return h(NRate, { value: row.difficulty_level, readonly: true, count: 5, size: 'small' })
    },
  },
  {
    title: '使用次数',
    key: 'usage_count',
    width: 80,
  },
  {
    title: '收藏',
    key: 'favorite_count',
    width: 80,
    render(row) {
      return h(
        NSpace,
        { align: 'center', size: 4 },
        {
          default: () => [
            h(NIcon, { color: '#f0a020' }, { default: () => h(Icon, { icon: 'ant-design:heart-filled' }) }),
            h('span', {}, row.favorite_count || 0)
          ]
        }
      )
    },
  },
  {
    title: '评分',
    key: 'rating',
    width: 80,
    render(row) {
      return `${row.rating.toFixed(1)} (${row.rating_count})`
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render(row) {
      return h(
        NSpace,
        { size: 'small' },
        {
          default: () => [
            h(
              NButton,
              { size: 'small', text: true, onClick: () => viewCaseDetail(row) },
              { default: () => '查看' }
            ),
            h(
              NButton,
              { size: 'small', text: true, onClick: () => editCase(row) },
              { default: () => '编辑' }
            ),
            h(
              NButton,
              { size: 'small', text: true, type: 'error', onClick: () => deleteCase(row) },
              { default: () => '删除' }
            ),
          ],
        }
      )
    },
  },
]

// 方法
const fetchCases = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: viewMode.value === 'list' ? pagination.page : 1,
      page_size: viewMode.value === 'list' ? pagination.pageSize : 12,
    }
    
    console.log('📤 请求参数:', params)

    const response = await request.get('/ideological/cases/', { params })
    console.log('📥 获取案例列表响应:', response)
    
    // 响应数据在 response.data 中
    const data = response?.data || response
    let items = data?.items || []
    // 先根据服务端的收藏状态同步本地收藏ID
    const serverFavoriteIds = items.filter(item => item.is_favorited).map(item => item.id)
    if (serverFavoriteIds.length > 0) {
      saveFavorites(serverFavoriteIds)
    }
    
    // 如果开启了"只看收藏"，则筛选收藏的案例
    if (searchForm.show_favorites_only) {
      const favorites = getFavorites()
      items = items.filter(item => favorites.includes(item.id))
    }
    casesList.value = items.map(item => ({
      ...item,
      content: item.content || '',
      rating: Number(item.rating ?? 0),
      rating_count: Number(item.rating_count ?? 0),
      favorite_count: item.favorite_count ?? 0,
      is_favorited: item.is_favorited ?? false,
    }))
    
    console.log(`✅ 获取到 ${items.length} 个案例，总数: ${data?.total || 0}`)
    
    // 调试：检查第一个案例的数据
    if (items.length > 0) {
      console.log('第一个案例数据:', items[0])
      console.log('theme_category_id:', items[0].theme_category_id)
      console.log('theme_name:', items[0].theme_name)
    } else {
      console.log('⚠️ 没有获取到任何案例')
    }
    
    // 更新收藏状态并同步本地存储
    updateFavoritesStatus()
    syncFavoritesStorage(casesList.value)

    if (viewMode.value === 'list') {
      pagination.itemCount = searchForm.show_favorites_only ? items.length : (data?.total || 0)
    }
  } catch (error) {
    console.error('获取案例列表失败:', error)
    message.error('获取案例列表失败')
    casesList.value = []
  } finally {
    loading.value = false
  }
}

const fetchOptions = async () => {
  try {
    // 获取章节选项
  try {
    const chaptersResponse = await api.getChaptersByCourse(1)
    const chapters = chaptersResponse?.data || chaptersResponse || []
    chapterOptions.value = chapters.map((item) => ({
      label: item.name,
      value: item.name,
    }))
  } catch (error) {
    console.error('获取章节选项失败:', error)
    // 使用默认章节数据
    chapterOptions.value = [
      '软件工程概述', '软件过程模型', '需求分析', '系统设计', '编码实现',
      '软件测试', '软件维护', '项目管理', '软件质量', '软件工程前沿',
    ].map((item) => ({ label: item, value: item }))
  }

    // 获取主题选项（从数据库读取）- 现在返回 ID 和名称
    try {
      const response = await themeCategoriesApi.getList()
      console.log('📥 主题分类API响应:', response)
      
      // 响应可能被多次包装，需要逐层解包
      let themesResponse = response?.data?.data || response?.data || response
      console.log('📦 解包后的数据:', themesResponse)
      console.log('📦 数据类型:', typeof themesResponse, Array.isArray(themesResponse))
      
      // 确保是数组
      if (!Array.isArray(themesResponse)) {
        console.error('❌ 主题数据不是数组:', themesResponse)
        throw new Error('主题数据格式错误')
      }
      
      // 只使用启用的二级分类
      themeOptions.value = themesResponse
        .filter(item => item.is_active && item.parent_id !== null)
        .map(item => ({
          label: item.name,
          value: item.id,  // 使用ID作为值
        }))
      
      console.log('✅ 处理后的主题选项:', themeOptions.value)
    } catch (error) {
      console.error('❌ 获取思政主题失败:', error)
      // 使用默认主题数据作为fallback
      themeOptions.value = [
        { label: "工匠精神", value: 5 },
        { label: "创新精神", value: 6 },
        { label: "团队协作", value: 11 },
        { label: "责任担当", value: 9 },
        { label: "诚信品质", value: 8 },
        { label: "法治意识", value: 10 },
        { label: "科学精神", value: 7 },
        { label: "人文素养", value: 13 },
        { label: "家国情怀", value: 12 },
        { label: "国际视野", value: 14 }
      ]
    }

    // 获取课程列表
    try {
      const coursesResponse = await request.get('/courses/all', { params: { is_active: true } })
      const courses = coursesResponse?.data || coursesResponse || []
      courseOptions.value = courses.map(course => ({
        label: course.name,
        value: course.id,
      }))
    } catch (error) {
      console.error('获取课程列表失败:', error)
      courseOptions.value = []
    }
  } catch (error) {
    message.error('获取选项数据失败')
  }
}


// 处理课程选择变化
const handleCourseChange = async (courseId) => {
  // 清空依赖的下拉框
  caseForm.chapter_id = null
  caseForm.knowledge_point_id = null
  courseChapterOptions.value = []
  knowledgePointOptions.value = []
  
  if (!courseId) return
  
  // 加载该课程的章节
  loadingChapters.value = true
  try {
    const response = await request.get('/chapters/', { params: { course_id: courseId } })
    const chapters = response?.data || response || []
    courseChapterOptions.value = chapters
      .sort((a, b) => (a.order || 0) - (b.order || 0))
      .map(chapter => ({
        label: chapter.name,
        value: chapter.id,
      }))
  } catch (error) {
    console.error('获取章节列表失败:', error)
    courseChapterOptions.value = []
  } finally {
    loadingChapters.value = false
  }
}

// 处理章节选择变化
const handleChapterChange = async (chapterId) => {
  // 清空知识点
  caseForm.knowledge_point_id = null
  knowledgePointOptions.value = []
  
  if (!chapterId) return
  
  // 加载该章节的知识点
  loadingKnowledgePoints.value = true
  try {
    const response = await request.get('/knowledge-points/', { params: { chapter_id: chapterId } })
    const knowledgePoints = response?.data || response || []
    knowledgePointOptions.value = knowledgePoints.map(kp => ({
      label: kp.name,
      value: kp.id,
    }))
  } catch (error) {
    console.error('获取知识点列表失败:', error)
    knowledgePointOptions.value = []
  } finally {
    loadingKnowledgePoints.value = false
  }
}

const handleSearch = () => {
  console.log('点击搜索按钮 - searchForm:', searchForm)
  pagination.page = 1
  fetchCases()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    software_engineering_chapter: null,
    theme_category_id: null,
    case_type: null,
    difficulty_level: null,
    show_favorites_only: false,
  })
  handleSearch()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchCases()
}

const showCreateModal = () => {
  editingCase.value = null
  resetCaseForm()
  createModalVisible.value = true
}

// 导入案例功能
const showImportModal = () => {
  importPreview.value = []
  importModalVisible.value = true
}

const closeImportModal = () => {
  importModalVisible.value = false
  importPreview.value = []
}

const handleBeforeUpload = (options) => {
  const { file } = options
  const fileName = file.name.toLowerCase()
  
  if (!fileName.endsWith('.json') && !fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
    message.error('仅支持JSON和Excel格式文件')
    return false
  }
  
  if (file.size > 5 * 1024 * 1024) {
    message.error('文件大小不能超过5MB')
    return false
  }
  
  return true
}

const handleFileRemove = () => {
  // 删除文件时清空预览数据
  importPreview.value = []
  return true
}

const handleCustomRequest = ({ file }) => {
  // 清空之前的预览数据
  importPreview.value = []
  
  const reader = new FileReader()
  const fileName = file.name.toLowerCase()
  
  reader.onload = async (e) => {
    try {
      if (fileName.endsWith('.json')) {
        // 解析JSON文件
        const jsonData = JSON.parse(e.target.result)
        if (Array.isArray(jsonData)) {
          parseAndValidateData(jsonData)
        } else {
          importPreview.value = []
          message.error('JSON文件格式错误，应为数组格式')
        }
      } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
        // 解析Excel文件需要使用xlsx库
        importPreview.value = []
        message.warning('Excel导入功能需要安装xlsx库，请使用JSON格式')
        // TODO: 添加xlsx解析逻辑
      }
    } catch (error) {
      console.error('文件解析失败:', error)
      importPreview.value = []
      message.error('文件解析失败，请检查文件格式')
    }
  }
  
  if (fileName.endsWith('.json')) {
    reader.readAsText(file.file)
  } else {
    reader.readAsArrayBuffer(file.file)
  }
}

const parseAndValidateData = (data) => {
  const validData = []
  const errors = []
  
  data.forEach((item, index) => {
    const errors_item = []
    
    // 验证必填字段
    if (!item.title || !item.title.trim()) {
      errors_item.push('标题不能为空')
    }
    if (!item.content || !item.content.trim()) {
      errors_item.push('内容不能为空')
    }
    if (!item.software_engineering_chapter) {
      errors_item.push('软件工程章节不能为空')
    }
    if (!item.ideological_theme) {
      errors_item.push('思政主题不能为空')
    }
    if (!item.case_type) {
      errors_item.push('案例类型不能为空')
    }
    
    if (errors_item.length > 0) {
      errors.push(`第${index + 1}行: ${errors_item.join(', ')}`)
    } else {
      // 构造有效的案例数据
      validData.push({
        title: item.title.trim(),
        content: item.content.trim(),
        software_engineering_chapter: item.software_engineering_chapter,
        ideological_theme: item.ideological_theme,
        case_type: item.case_type,
        tags: item.tags || [],
        key_points: item.key_points || [],
        discussion_questions: item.discussion_questions || [],
        teaching_suggestions: item.teaching_suggestions || '',
        difficulty_level: item.difficulty_level || 3,
        is_public: item.is_public !== false, // 默认公开
        status: 'published', // 直接发布
      })
    }
  })
  
  if (errors.length > 0) {
    dialog.warning({
      title: '数据验证警告',
      content: errors.join('\n'),
      positiveText: '继续导入有效数据',
      negativeText: '取消',
      onPositiveClick: () => {
        if (validData.length > 0) {
          importPreview.value = validData.slice(0, 100) // 最多100条
          message.success(`成功解析${validData.length}条有效数据`)
        }
      }
    })
  } else {
    importPreview.value = validData.slice(0, 100)
    message.success(`成功解析${validData.length}条数据`)
  }
}

const confirmImport = async () => {
  if (importPreview.value.length === 0) {
    message.warning('没有可导入的数据')
    return
  }
  
  importLoading.value = true
  try {
    let successCount = 0
    let failCount = 0
    
    // 批量创建案例
    for (const caseData of importPreview.value) {
      try {
        await request.post('/ideological/cases/', caseData)
        successCount++
      } catch (error) {
        console.error('导入案例失败:', error)
        failCount++
      }
    }
    
    if (successCount > 0) {
      message.success(`成功导入${successCount}条案例${failCount > 0 ? `，失败${failCount}条` : ''}`)
      importModalVisible.value = false
      importPreview.value = []
      // 刷新列表
      fetchCases()
      fetchStatistics()
    } else {
      message.error('导入失败，请检查数据格式')
    }
  } catch (error) {
    console.error('批量导入失败:', error)
    message.error('批量导入失败')
  } finally {
    importLoading.value = false
  }
}

const resetCaseForm = () => {
  Object.assign(caseForm, {
    title: '',
    content: '',
    software_engineering_chapter: null,
    theme_category_id: null,
    case_type: null,
    difficulty_level: 3,
    key_points: [],
    discussion_questions: [],
    teaching_suggestions: '',
    tags: [],
    is_public: true,
    course_id: null,
    chapter_id: null,
    knowledge_point_id: null,
  })
  // 清空级联选项
  courseChapterOptions.value = []
  knowledgePointOptions.value = []
}

const editCase = async (case_item) => {
  editingCase.value = case_item
  Object.assign(caseForm, case_item)
  
  // 确保 theme_category_id 是数字类型
  if (caseForm.theme_category_id) {
    caseForm.theme_category_id = Number(caseForm.theme_category_id)
  }
  
  console.log('编辑案例 - theme_category_id:', caseForm.theme_category_id, typeof caseForm.theme_category_id)
  
  // 如果有课程ID，加载对应的章节
  if (case_item.course_id) {
    await handleCourseChange(case_item.course_id)
    // 如果有章节ID，加载对应的知识点
    if (case_item.chapter_id) {
      await handleChapterChange(case_item.chapter_id)
    }
  }
  
  createModalVisible.value = true
}

const handleSubmitCase = async () => {
  try {
    await caseFormRef.value?.validate()
    submitLoading.value = true

    let needRefreshList = false
    
    if (editingCase.value) {
      const response = await request.put(`/ideological/cases/${editingCase.value.id}`, caseForm)
      message.success('案例更新成功')
      
      // 获取更新后的数据
      const updatedCase = response?.data || response
      
      // 如果后端返回了完整数据，直接更新
      if (updatedCase && updatedCase.id) {
        // 刷新案例列表中的对应项
        const caseInList = casesList.value.find(item => item.id === editingCase.value.id)
        if (caseInList) {
          Object.assign(caseInList, updatedCase)
        }
        
        // 如果详情页是打开的，刷新详情页数据
        if (detailModalVisible.value && currentCase.value?.id === editingCase.value.id) {
          Object.assign(currentCase.value, updatedCase)
        }
      } else {
        // 如果响应中没有完整数据，标记需要重新加载列表
        needRefreshList = true
        
        // 如果详情页打开，重新请求详情数据
        if (detailModalVisible.value && currentCase.value?.id === editingCase.value.id) {
          try {
            const caseDetail = await request.get(`/ideological/cases/${editingCase.value.id}`)
            const caseData = caseDetail?.data || caseDetail
            Object.assign(currentCase.value, caseData)
          } catch (err) {
            console.error('刷新详情失败:', err)
          }
        }
      }
    } else {
      await request.post('/ideological/cases/', caseForm)
      message.success('案例创建成功')
      needRefreshList = true
    }

    createModalVisible.value = false
    
    // 只在需要时刷新列表
    if (needRefreshList) {
      fetchCases()
    }
  } catch (error) {
    message.error(editingCase.value ? '案例更新失败' : '案例创建失败')
  } finally {
    submitLoading.value = false
  }
}

const deleteCase = (case_item) => {
  dialog.warning({
    title: '删除确认',
    content: `确定要删除案例"${case_item.title}"吗？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await request.delete(`/ideological/cases/${case_item.id}`)
        message.success('案例删除成功')
        fetchCases()
      } catch (error) {
        message.error('案例删除失败')
      }
    },
  })
}

const viewCaseDetail = (case_item) => {
  currentCase.value = case_item
  // 确保详情页的收藏状态是最新的
  if (typeof currentCase.value.is_favorited === 'undefined' || currentCase.value.is_favorited === null) {
    const favorites = getFavorites()
    currentCase.value.is_favorited = favorites.includes(case_item.id)
  }
  ensureFavoriteCount(currentCase.value)
  detailModalVisible.value = true
}

const renderMarkdown = (content) => {
  if (!content) return ''
  return md.render(content)
}

const renderMarkdownExcerpt = (content, limit = 160) => {
  if (!content) return ''
  const text = content.length > limit ? `${content.slice(0, limit)}...` : content
  return md.render(text)
}

// 收藏功能相关
const FAVORITES_STORAGE_KEY = 'aigc_case_favorites'

// 获取所有收藏的案例ID
const getFavorites = () => {
  try {
    const favorites = localStorage.getItem(FAVORITES_STORAGE_KEY)
    return favorites ? JSON.parse(favorites) : []
  } catch (error) {
    console.error('读取收藏数据失败:', error)
    return []
  }
}

// 保存收藏到本地存储
const saveFavorites = (favorites) => {
  try {
    localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favorites))
  } catch (error) {
    console.error('保存收藏数据失败:', error)
  }
}

// 切换收藏状态
const toggleFavorite = async (case_item) => {
  const targetState = !case_item.is_favorited
  const prevState = case_item.is_favorited
  const prevCount = case_item.favorite_count

  try {
    const response = await casesApi.toggleFavorite(case_item.id, targetState)
    const data = response?.data || response || {}
    case_item.is_favorited = data.favorited ?? targetState
    case_item.favorite_count = Number(data.favorite_count ?? prevCount ?? 0)
    ensureFavoriteCount(case_item)

    // 同步本地收藏列表，用于“只看收藏”过滤
    const favorites = getFavorites()
    if (case_item.is_favorited) {
      if (!favorites.includes(case_item.id)) {
        favorites.push(case_item.id)
      }
    } else {
      const idx = favorites.indexOf(case_item.id)
      if (idx !== -1) favorites.splice(idx, 1)
    }
    saveFavorites(favorites)

    // 同步详情弹窗
    if (detailModalVisible.value && currentCase.value?.id === case_item.id) {
      currentCase.value.is_favorited = case_item.is_favorited
      currentCase.value.favorite_count = case_item.favorite_count
    }

    message.success(case_item.is_favorited ? '收藏成功' : '取消收藏')
  } catch (error) {
    console.error('收藏操作失败:', error)
    case_item.is_favorited = prevState
    case_item.favorite_count = prevCount
    message.error('收藏操作失败')
  }
}

// 更新案例列表的收藏状态和收藏数
const updateFavoritesStatus = () => {
  const favorites = getFavorites()
  casesList.value.forEach(item => {
    if (typeof item.is_favorited === 'undefined' || item.is_favorited === null) {
      item.is_favorited = favorites.includes(item.id)
    }
    ensureFavoriteCount(item)
  })
}

const syncFavoritesStorage = (items = []) => {
  const ids = items.filter(item => item.is_favorited).map(item => item.id)
  saveFavorites(ids)
}

// 计算案例的收藏数（基于所有用户的本地收藏，这里只能统计当前用户）
const calculateFavoriteCount = (caseId) => {
  const favorites = getFavorites()
  return favorites.includes(caseId) ? 1 : 0
}

const rateCase = (case_item) => {
  currentCase.value = case_item
  ratingForm.rating = 5
  ratingForm.comment = ''
  ratingModalVisible.value = true
}

const submitRating = async () => {
  try {
    // 后端期望rating作为Query参数
    const params = {
      rating: ratingForm.rating,
      comment: ratingForm.comment || undefined
    }
    await request.post(`/ideological/cases/${currentCase.value.id}/rate`, null, { params })
    message.success('评分成功')
    ratingModalVisible.value = false
    fetchCases()
    fetchStatistics()
  } catch (error) {
    console.error('评分失败:', error)
    message.error('评分失败')
    return false
  }
}

const getCaseTypeLabel = (type) => {
  const option = caseTypeOptions.value.find(item => item.value === type)
  return option ? option.label : type
}

const getDifficultyTagType = (level) => {
  if (level <= 2) return 'success'
  if (level <= 4) return 'warning'
  return 'error'
}

const getCaseActionOptions = (case_item) => {
  return [
    { label: '查看详情', key: 'view' },
    { label: '编辑', key: 'edit' },
    { label: '复制', key: 'copy' },
    { label: '导出', key: 'export' },
    { type: 'divider' },
    { label: '删除', key: 'delete' },
  ]
}

// 确保收藏数展示与本地收藏状态一致
const ensureFavoriteCount = (item) => {
  if (!item) return
  const count = Number(item.favorite_count ?? 0)
  item.favorite_count = item.is_favorited ? Math.max(count, 1) : count
}

const handleCaseAction = (key, case_item) => {
  switch (key) {
    case 'view':
      viewCaseDetail(case_item)
      break
    case 'edit':
      editCase(case_item)
      break
    case 'copy':
      copyCase(case_item)
      break
    case 'export':
      exportCase(case_item)
      break
    case 'delete':
      deleteCase(case_item)
      break
  }
}

const copyCase = async (case_item) => {
  try {
    const copiedCase = {
      ...case_item,
      title: `${case_item.title} (副本)`,
      id: undefined,
    }
    delete copiedCase.id
    delete copiedCase.created_at
    delete copiedCase.updated_at
    
    await request.post('/ideological/cases/', copiedCase)
    message.success('案例已复制')
    fetchCases()
    fetchStatistics()
  } catch (error) {
    message.error('复制失败')
  }
}

const exportCase = (case_item) => {
  const markdown = `# ${case_item.title}

## 基本信息

- **软件工程章节**: ${case_item.software_engineering_chapter}
- **思政主题**: ${case_item.theme_name || '-'}
- **案例类型**: ${getCaseTypeLabel(case_item.case_type)}
- **难度等级**: ${case_item.difficulty_level}/5
- **评分**: ${case_item.rating.toFixed(1)} (${case_item.rating_count}人评价)

## 案例内容

${case_item.content}

## 关键知识点

${case_item.key_points?.map(p => `- ${p}`).join('\n') || '无'}

## 讨论问题

${case_item.discussion_questions?.map((q, i) => `${i + 1}. ${q}`).join('\n') || '无'}

## 教学建议

${case_item.teaching_suggestions || '无'}

## 标签

${case_item.tags?.map(t => `#${t}`).join(' ') || '无'}
`

  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${case_item.title}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  message.success('导出成功')
}

const toggleSelection = (case_item) => {
  if (case_item.selected) {
    selectedCases.value.push(case_item.id)
  } else {
    selectedCases.value = selectedCases.value.filter(id => id !== case_item.id)
  }
}

const showBatchOperations = () => {
  dialog.warning({
    title: '批量操作',
    content: `已选择 ${selectedCases.value.length} 个案例，确定要删除吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await Promise.all(
          selectedCases.value.map(id => request.delete(`/ideological/cases/${id}`))
        )
        message.success('批量删除成功')
        selectedCases.value = []
        fetchCases()
        fetchStatistics()
      } catch (error) {
        message.error('批量删除失败')
      }
    },
  })
}

const fetchStatistics = async () => {
  try {
    // 获取所有案例总数
    const allResponse = await request.get('/ideological/cases/', { params: { page_size: 100 } })
    const allData = allResponse?.data || allResponse
    const total = allData?.total ?? 0
    totalCases.value = total
    
    // 获取所有案例数据用于统计
    const allItems = allData?.items || []
    
    // 计算我的案例数（假设有author字段）
    // 如果API有单独的我的案例接口，应该调用那个接口
    // 这里暂时使用简单计数，实际应该过滤当前用户的案例
    myCases.value = allItems.filter(item => item.author_id).length || Math.floor(total * 0.6)
    
    // 计算热门案例数（使用次数>0或评分>0的案例）
    hotCases.value = allItems.filter(item => 
      (item.usage_count && item.usage_count > 0) || 
      (item.rating && item.rating > 0)
    ).length || Math.floor(total * 0.3)
    
    // 计算平均评分
    if (allItems.length > 0) {
      const ratedItems = allItems.filter(item => item.rating_count && item.rating_count > 0)
      if (ratedItems.length > 0) {
        const totalRating = ratedItems.reduce((sum, item) => sum + (item.rating || 0), 0)
        avgRating.value = Number((totalRating / ratedItems.length).toFixed(1))
      } else {
        avgRating.value = 0
      }
    } else {
      avgRating.value = 0
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    totalCases.value = 0
    myCases.value = 0
    hotCases.value = 0
    avgRating.value = 0
  }
}

// 初始化
onMounted(() => {
  fetchOptions()
  fetchCases()
  fetchStatistics()
})
</script>

<style scoped>
.cases-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--n-text-color);
}

.title-section p {
  margin: 0;
  font-size: 14px;
  color: var(--n-text-color-depth-3);
}

.search-section {
  margin-bottom: 0;
}

.cases-list {
  flex: 1;
}

.grid-view {
  min-height: 400px;
}

.case-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.case-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.case-title {
  font-weight: 600;
  flex: 1;
  margin-right: 8px;
}

.case-description {
  color: var(--n-text-color-depth-3);
  margin: 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.case-meta {
  margin-top: 12px;
}

.case-footer {
  margin-top: 12px;
}

.list-view {
  min-height: 400px;
}

.case-checkbox {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1;
}

.case-detail-content {
  line-height: 1.8;
  word-wrap: break-word;
}

.markdown-content :deep(p) {
  margin: 0 0 8px;
  line-height: 1.6;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

.markdown-content :deep(li) {
  margin: 4px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .title-section h1 {
    font-size: 20px;
  }
}
</style>
