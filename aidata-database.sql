/*
 Navicat Premium Dump SQL

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80036 (8.0.36)
 Source Host           : localhost:3306
 Source Schema         : aidata

 Target Server Type    : MySQL
 Target Server Version : 80036 (8.0.36)
 File Encoding         : 65001

 Date: 02/01/2026 15:02:50
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for aerich
-- ----------------------------
DROP TABLE IF EXISTS `aerich`;
CREATE TABLE `aerich`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `version` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `app` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `content` json NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 20 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for api
-- ----------------------------
DROP TABLE IF EXISTS `api`;
CREATE TABLE `api`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `path` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'API路径',
  `method` varchar(6) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '请求方法',
  `summary` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '请求简介',
  `tags` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'API标签',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_api_created_78d19f`(`created_at` ASC) USING BTREE,
  INDEX `idx_api_updated_643c8b`(`updated_at` ASC) USING BTREE,
  INDEX `idx_api_path_9ed611`(`path` ASC) USING BTREE,
  INDEX `idx_api_method_a46dfb`(`method` ASC) USING BTREE,
  INDEX `idx_api_summary_400f73`(`summary` ASC) USING BTREE,
  INDEX `idx_api_tags_04ae27`(`tags` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 96 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for auditlog
-- ----------------------------
DROP TABLE IF EXISTS `auditlog`;
CREATE TABLE `auditlog`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `user_id` int NOT NULL COMMENT '用户ID',
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '用户名称',
  `module` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '功能模块',
  `summary` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '请求描述',
  `method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '请求方法',
  `path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '' COMMENT '请求路径',
  `status` int NOT NULL DEFAULT -1 COMMENT '状态码',
  `response_time` int NOT NULL DEFAULT 0 COMMENT '响应时间(单位ms)',
  `request_args` json NULL COMMENT '请求参数',
  `response_body` json NULL COMMENT '返回数据',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_auditlog_created_cc33d0`(`created_at` ASC) USING BTREE,
  INDEX `idx_auditlog_updated_2f871f`(`updated_at` ASC) USING BTREE,
  INDEX `idx_auditlog_user_id_4b93fa`(`user_id` ASC) USING BTREE,
  INDEX `idx_auditlog_usernam_b187b3`(`username` ASC) USING BTREE,
  INDEX `idx_auditlog_module_04058b`(`module` ASC) USING BTREE,
  INDEX `idx_auditlog_summary_3e27da`(`summary` ASC) USING BTREE,
  INDEX `idx_auditlog_method_4270a2`(`method` ASC) USING BTREE,
  INDEX `idx_auditlog_path_b99502`(`path` ASC) USING BTREE,
  INDEX `idx_auditlog_status_2a72d2`(`status` ASC) USING BTREE,
  INDEX `idx_auditlog_respons_8caa87`(`response_time` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3941 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for chapter_case_rel
-- ----------------------------
DROP TABLE IF EXISTS `chapter_case_rel`;
CREATE TABLE `chapter_case_rel`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `case_id` bigint NOT NULL COMMENT '案例ID',
  `chapter_id` bigint NOT NULL COMMENT '章节ID',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_case`(`case_id` ASC) USING BTREE,
  INDEX `idx_chapter`(`chapter_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '章节-案例关联表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for chapters
-- ----------------------------
DROP TABLE IF EXISTS `chapters`;
CREATE TABLE `chapters`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `course_id` bigint NOT NULL COMMENT '课程ID',
  `parent_id` bigint NOT NULL DEFAULT 0 COMMENT '父章节ID，0表示顶级章节',
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '章节名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '章节描述',
  `order` int NOT NULL DEFAULT 0 COMMENT '排序',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_course`(`course_id` ASC) USING BTREE,
  INDEX `idx_parent`(`parent_id` ASC) USING BTREE,
  INDEX `idx_order`(`order` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '章节表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '课程代码',
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '课程名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '课程描述',
  `credit` decimal(3, 1) NULL DEFAULT NULL COMMENT '学分',
  `hours` int NULL DEFAULT NULL COMMENT '学时',
  `semester` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '开课学期',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `created_by_id` bigint NULL DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_code`(`code` ASC) USING BTREE,
  INDEX `idx_name`(`name` ASC) USING BTREE,
  INDEX `idx_is_active`(`is_active` ASC) USING BTREE,
  INDEX `idx_created_by`(`created_by_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '课程表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for generation_history
-- ----------------------------
DROP TABLE IF EXISTS `generation_history`;
CREATE TABLE `generation_history`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `user_input` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户输入',
  `generated_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '生成内容',
  `generation_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '生成类型',
  `software_engineering_chapter` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '软件工程章节',
  `ideological_theme` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '思政主题',
  `course_id` bigint NULL DEFAULT NULL COMMENT '课程ID',
  `chapter_id` bigint NULL DEFAULT NULL COMMENT '章节ID',
  `token_count` int NULL DEFAULT NULL COMMENT 'Token消耗数量',
  `generation_time` int NULL DEFAULT NULL COMMENT '生成耗时(毫秒)',
  `user_rating` int NULL DEFAULT NULL COMMENT '用户评分(1-5)',
  `user_feedback` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '用户反馈',
  `is_saved_to_case` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否已保存为案例',
  `case_id` bigint NULL DEFAULT NULL,
  `prompt_template_id` bigint NULL DEFAULT NULL,
  `user_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_generati_ideologi_7855dbd1`(`case_id` ASC) USING BTREE,
  INDEX `fk_generati_prompt_t_48a9e3a0`(`prompt_template_id` ASC) USING BTREE,
  INDEX `fk_generati_user_7b2e0a50`(`user_id` ASC) USING BTREE,
  INDEX `fk_generati_courses_9b9f2a`(`course_id` ASC) USING BTREE,
  INDEX `fk_generati_chapters_7b40ef`(`chapter_id` ASC) USING BTREE,
  INDEX `idx_generation__created_843a78`(`created_at` ASC) USING BTREE,
  INDEX `idx_generation__updated_daab7f`(`updated_at` ASC) USING BTREE,
  INDEX `idx_generation__generat_2eb071`(`generation_type` ASC) USING BTREE,
  INDEX `idx_generation__softwar_7dfc7b`(`software_engineering_chapter` ASC) USING BTREE,
  INDEX `idx_generation__ideolog_cc61ab`(`ideological_theme` ASC) USING BTREE,
  INDEX `idx_generation__user_ra_e4899d`(`user_rating` ASC) USING BTREE,
  INDEX `idx_generation__is_save_2c1be4`(`is_saved_to_case` ASC) USING BTREE,
  CONSTRAINT `fk_generati_chapters_7b40ef` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_generati_courses_9b9f2a` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_generati_ideologi_7855dbd1` FOREIGN KEY (`case_id`) REFERENCES `ideological_case` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_generati_prompt_t_48a9e3a0` FOREIGN KEY (`prompt_template_id`) REFERENCES `prompt_template` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_generati_user_7b2e0a50` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 47 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '生成历史记录' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for ideological_case
-- ----------------------------
DROP TABLE IF EXISTS `ideological_case`;
CREATE TABLE `ideological_case`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '案例标题',
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '案例内容',
  `software_engineering_chapter` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '软件工程章节',
  `course_id` bigint NULL DEFAULT NULL COMMENT '课程ID',
  `chapter_id` bigint NULL DEFAULT NULL COMMENT '章节ID',
  `case_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '案例类型',
  `tags` json NOT NULL COMMENT '标签列表',
  `key_points` json NOT NULL COMMENT '关键知识点',
  `discussion_questions` json NOT NULL COMMENT '讨论问题',
  `teaching_suggestions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '教学建议',
  `difficulty_level` int NOT NULL DEFAULT 1 COMMENT '难度等级(1-5)',
  `usage_count` int NOT NULL DEFAULT 0 COMMENT '使用次数',
  `rating` double NOT NULL DEFAULT 0 COMMENT '评分(0-5)',
  `rating_count` int NOT NULL DEFAULT 0 COMMENT '评分人数',
  `is_public` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否公开',
  `status` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'draft' COMMENT '状态',
  `reviewer_comment` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '审核意见',
  `author_id` bigint NULL DEFAULT NULL,
  `reviewer_id` bigint NULL DEFAULT NULL,
  `theme_category_id` int NULL DEFAULT NULL COMMENT '思政主题分类ID',
  `favorite_count` int NOT NULL DEFAULT 0 COMMENT '收藏次数',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_ideologi_user_c416c751`(`author_id` ASC) USING BTREE,
  INDEX `fk_ideologi_user_4c003c04`(`reviewer_id` ASC) USING BTREE,
  INDEX `idx_ideological_created_1a35a2`(`created_at` ASC) USING BTREE,
  INDEX `idx_ideological_updated_5486c3`(`updated_at` ASC) USING BTREE,
  INDEX `idx_ideological_title_87831e`(`title` ASC) USING BTREE,
  INDEX `idx_ideological_softwar_335d07`(`software_engineering_chapter` ASC) USING BTREE,
  INDEX `fk_ideological_course_9b6f6b`(`course_id` ASC) USING BTREE,
  INDEX `fk_ideological_chapter_3e0f63`(`chapter_id` ASC) USING BTREE,
  INDEX `idx_ideological_case_ty_9e4f16`(`case_type` ASC) USING BTREE,
  INDEX `idx_ideological_difficu_a3a547`(`difficulty_level` ASC) USING BTREE,
  INDEX `idx_ideological_usage_c_3d3b48`(`usage_count` ASC) USING BTREE,
  INDEX `idx_ideological_rating_2f80a2`(`rating` ASC) USING BTREE,
  INDEX `idx_ideological_rating__3c8fec`(`rating_count` ASC) USING BTREE,
  INDEX `idx_ideological_is_publ_3c2735`(`is_public` ASC) USING BTREE,
  INDEX `idx_ideological_status_d2bcec`(`status` ASC) USING BTREE,
  INDEX `idx_ideological_theme_c_5cff9e`(`theme_category_id` ASC) USING BTREE,
  INDEX `idx_ideological_favorit_dc84a6`(`favorite_count` ASC) USING BTREE,
  CONSTRAINT `fk_ideologi_user_4c003c04` FOREIGN KEY (`reviewer_id`) REFERENCES `user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_ideologi_user_c416c751` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_ideological_chapter_3e0f63` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_ideological_course_9b6f6b` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 28 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '课程思政案例库' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for ideological_theme_categories
-- ----------------------------
DROP TABLE IF EXISTS `ideological_theme_categories`;
CREATE TABLE `ideological_theme_categories`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '分类名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '分类描述',
  `parent_id` int NULL DEFAULT NULL COMMENT '父分类ID',
  `order` int NOT NULL DEFAULT 0 COMMENT '排序',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_name`(`name` ASC) USING BTREE,
  INDEX `idx_parent_id`(`parent_id` ASC) USING BTREE,
  INDEX `idx_order`(`order` ASC) USING BTREE,
  INDEX `idx_is_active`(`is_active` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '思政主题分类表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for knowledge_points
-- ----------------------------
DROP TABLE IF EXISTS `knowledge_points`;
CREATE TABLE `knowledge_points`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `chapter_id` bigint NOT NULL COMMENT '章节ID',
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '知识点名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '知识点描述',
  `difficulty` int NOT NULL DEFAULT 3 COMMENT '难度等级1-5',
  `importance` int NOT NULL DEFAULT 3 COMMENT '重要程度1-5',
  `keywords` json NULL COMMENT '关键词',
  `order` int NOT NULL DEFAULT 0 COMMENT '排序',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_chapter`(`chapter_id` ASC) USING BTREE,
  INDEX `idx_order`(`order` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 83 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '知识点表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for menu
-- ----------------------------
DROP TABLE IF EXISTS `menu`;
CREATE TABLE `menu`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '菜单名称',
  `remark` json NULL COMMENT '保留字段',
  `menu_type` varchar(7) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '菜单类型',
  `icon` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '菜单图标',
  `path` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '菜单路径',
  `order` int NOT NULL DEFAULT 0 COMMENT '排序',
  `parent_id` int NOT NULL DEFAULT 0 COMMENT '父菜单ID',
  `is_hidden` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否隐藏',
  `component` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '组件',
  `keepalive` tinyint(1) NOT NULL DEFAULT 1 COMMENT '存活',
  `redirect` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '重定向',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
  `deleted_at` datetime(6) NULL DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_menu_created_b6922b`(`created_at` ASC) USING BTREE,
  INDEX `idx_menu_updated_e6b0a1`(`updated_at` ASC) USING BTREE,
  INDEX `idx_menu_name_b9b853`(`name` ASC) USING BTREE,
  INDEX `idx_menu_path_bf95b2`(`path` ASC) USING BTREE,
  INDEX `idx_menu_order_606068`(`order` ASC) USING BTREE,
  INDEX `idx_menu_parent__bebd15`(`parent_id` ASC) USING BTREE,
  INDEX `idx_menu_is_dele_784167`(`is_deleted` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for prompt_assistant_conversation
-- ----------------------------
DROP TABLE IF EXISTS `prompt_assistant_conversation`;
CREATE TABLE `prompt_assistant_conversation`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `session_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '会话ID',
  `user_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户消息',
  `assistant_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '助手回复',
  `session_stage` varchar(21) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'greeting' COMMENT '会话阶段',
  `extracted_requirements` json NOT NULL COMMENT '提取的需求信息',
  `suggested_prompt` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '建议的提示词',
  `user_feedback` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '用户反馈',
  `is_final_prompt_generated` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否已生成最终提示词',
  `final_prompt` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '最终生成的提示词',
  `token_count` int NULL DEFAULT NULL COMMENT 'Token消耗数量',
  `generation_time` int NULL DEFAULT NULL COMMENT '生成耗时(毫秒)',
  `user_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_prompt_a_user_f632c4a3`(`user_id` ASC) USING BTREE,
  INDEX `idx_prompt_assi_created_f18434`(`created_at` ASC) USING BTREE,
  INDEX `idx_prompt_assi_updated_660d4d`(`updated_at` ASC) USING BTREE,
  INDEX `idx_prompt_assi_session_2f6a9a`(`session_id` ASC) USING BTREE,
  CONSTRAINT `fk_prompt_a_user_f632c4a3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 17 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '提示词助手对话记录' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for prompt_assistant_template
-- ----------------------------
DROP TABLE IF EXISTS `prompt_assistant_template`;
CREATE TABLE `prompt_assistant_template`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模板名称',
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模板描述',
  `template_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模板类型',
  `target_audience` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '目标受众',
  `use_case_scenario` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '使用场景',
  `sample_prompts` json NOT NULL COMMENT '示例提示词列表',
  `key_questions` json NOT NULL COMMENT '关键问题列表',
  `best_practices` json NOT NULL COMMENT '最佳实践列表',
  `common_variables` json NOT NULL COMMENT '常用变量列表',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `usage_count` int NOT NULL DEFAULT 0 COMMENT '使用次数',
  `rating` double NOT NULL DEFAULT 0 COMMENT '评分(0-5)',
  `rating_count` int NOT NULL DEFAULT 0 COMMENT '评分人数',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_prompt_assi_created_bbd3f8`(`created_at` ASC) USING BTREE,
  INDEX `idx_prompt_assi_updated_d8a557`(`updated_at` ASC) USING BTREE,
  INDEX `idx_prompt_assi_name_a80cdf`(`name` ASC) USING BTREE,
  INDEX `idx_prompt_assi_templat_d6e9bd`(`template_type` ASC) USING BTREE,
  INDEX `idx_prompt_assi_is_acti_a5bb3e`(`is_active` ASC) USING BTREE,
  INDEX `idx_prompt_assi_usage_c_3f52be`(`usage_count` ASC) USING BTREE,
  INDEX `idx_prompt_assi_rating_720191`(`rating` ASC) USING BTREE,
  INDEX `idx_prompt_assi_rating__66e1be`(`rating_count` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1399 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '提示词助手预置模板' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for prompt_template
-- ----------------------------
DROP TABLE IF EXISTS `prompt_template`;
CREATE TABLE `prompt_template`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模板名称',
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模板描述',
  `template_type` varchar(21) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模板类型',
  `template_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模板内容',
  `variables` json NOT NULL COMMENT '模板变量',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '分类',
  `software_engineering_chapter` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '适用章节',
  `usage_count` int NOT NULL DEFAULT 0 COMMENT '使用次数',
  `is_system` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否系统模板',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
  `rating` double NOT NULL DEFAULT 0 COMMENT '评分(0-5)',
  `rating_count` int NOT NULL DEFAULT 0 COMMENT '评分人数',
  `creator_id` bigint NULL DEFAULT NULL,
  `theme_category_id` int NULL DEFAULT NULL COMMENT '思政主题分类ID',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_prompt_t_user_f74eb6b9`(`creator_id` ASC) USING BTREE,
  INDEX `idx_prompt_temp_created_bf7a5c`(`created_at` ASC) USING BTREE,
  INDEX `idx_prompt_temp_updated_c0e4a3`(`updated_at` ASC) USING BTREE,
  INDEX `idx_prompt_temp_name_941a49`(`name` ASC) USING BTREE,
  INDEX `idx_prompt_temp_templat_8bae9a`(`template_type` ASC) USING BTREE,
  INDEX `idx_prompt_temp_categor_14337a`(`category` ASC) USING BTREE,
  INDEX `idx_prompt_temp_softwar_112694`(`software_engineering_chapter` ASC) USING BTREE,
  INDEX `idx_prompt_temp_usage_c_fbd1b0`(`usage_count` ASC) USING BTREE,
  INDEX `idx_prompt_temp_is_syst_d91c18`(`is_system` ASC) USING BTREE,
  INDEX `idx_prompt_temp_is_acti_8b5a28`(`is_active` ASC) USING BTREE,
  INDEX `idx_prompt_temp_rating_0729e6`(`rating` ASC) USING BTREE,
  INDEX `idx_prompt_temp_rating__5eed95`(`rating_count` ASC) USING BTREE,
  INDEX `idx_prompt_temp_theme_c_888f33`(`theme_category_id` ASC) USING BTREE,
  CONSTRAINT `fk_prompt_t_user_f74eb6b9` FOREIGN KEY (`creator_id`) REFERENCES `user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '提示词模板库' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for role
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '角色名称',
  `desc` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '角色描述',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  INDEX `idx_role_created_7f5f71`(`created_at` ASC) USING BTREE,
  INDEX `idx_role_updated_5dd337`(`updated_at` ASC) USING BTREE,
  INDEX `idx_role_name_e5618b`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for role_api
-- ----------------------------
DROP TABLE IF EXISTS `role_api`;
CREATE TABLE `role_api`  (
  `role_id` bigint NOT NULL,
  `api_id` bigint NOT NULL,
  UNIQUE INDEX `uidx_role_api_role_id_ba4286`(`role_id` ASC, `api_id` ASC) USING BTREE,
  INDEX `api_id`(`api_id` ASC) USING BTREE,
  CONSTRAINT `role_api_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `role_api_ibfk_2` FOREIGN KEY (`api_id`) REFERENCES `api` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for role_menu
-- ----------------------------
DROP TABLE IF EXISTS `role_menu`;
CREATE TABLE `role_menu`  (
  `role_id` bigint NOT NULL,
  `menu_id` bigint NOT NULL,
  UNIQUE INDEX `uidx_role_menu_role_id_90801c`(`role_id` ASC, `menu_id` ASC) USING BTREE,
  INDEX `menu_id`(`menu_id` ASC) USING BTREE,
  CONSTRAINT `role_menu_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `role_menu_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `menu` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for teaching_resource
-- ----------------------------
DROP TABLE IF EXISTS `teaching_resource`;
CREATE TABLE `teaching_resource`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '资源标题',
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '资源描述',
  `resource_type` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '资源类型',
  `file_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '文件URL',
  `file_size` int NULL DEFAULT NULL COMMENT '文件大小(字节)',
  `file_format` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '文件格式',
  `download_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '下载链接',
  `preview_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '预览链接',
  `external_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '外部链接',
  `tags` json NOT NULL COMMENT '标签列表',
  `software_engineering_chapter` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '适用章节',
  `course_id` bigint NULL DEFAULT NULL COMMENT '课程ID',
  `chapter_id` bigint NULL DEFAULT NULL COMMENT '章节ID',
  `usage_count` int NOT NULL DEFAULT 0 COMMENT '使用次数',
  `is_public` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否公开',
  `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '文件路径',
  `uploader_id` bigint NULL DEFAULT NULL,
  `theme_category_id` int NULL DEFAULT NULL COMMENT '思政主题分类ID',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_teaching_user_64e08528`(`uploader_id` ASC) USING BTREE,
  INDEX `idx_teaching_re_created_40a43a`(`created_at` ASC) USING BTREE,
  INDEX `idx_teaching_re_updated_3fa91e`(`updated_at` ASC) USING BTREE,
  INDEX `idx_teaching_re_title_396904`(`title` ASC) USING BTREE,
  INDEX `idx_teaching_re_resourc_f1ce22`(`resource_type` ASC) USING BTREE,
  INDEX `idx_teaching_re_softwar_9b0ab0`(`software_engineering_chapter` ASC) USING BTREE,
  INDEX `fk_teaching_resource_course_f1e0a0`(`course_id` ASC) USING BTREE,
  INDEX `fk_teaching_resource_chapter_6b1e2f`(`chapter_id` ASC) USING BTREE,
  INDEX `idx_teaching_re_usage_c_458ddf`(`usage_count` ASC) USING BTREE,
  INDEX `idx_teaching_re_is_publ_5f4125`(`is_public` ASC) USING BTREE,
  INDEX `idx_teaching_re_theme_c_8244aa`(`theme_category_id` ASC) USING BTREE,
  CONSTRAINT `fk_teaching_resource_chapter_6b1e2f` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_teaching_resource_course_f1e0a0` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_teaching_user_64e08528` FOREIGN KEY (`uploader_id`) REFERENCES `user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '教学资源库' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名称',
  `alias` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '姓名',
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '邮箱',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '电话',
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '密码',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  `is_superuser` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否为超级管理员',
  `last_login` datetime(6) NULL DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE,
  INDEX `idx_user_created_b19d59`(`created_at` ASC) USING BTREE,
  INDEX `idx_user_updated_dfdb43`(`updated_at` ASC) USING BTREE,
  INDEX `idx_user_usernam_9987ab`(`username` ASC) USING BTREE,
  INDEX `idx_user_alias_6f9868`(`alias` ASC) USING BTREE,
  INDEX `idx_user_email_1b4f1c`(`email` ASC) USING BTREE,
  INDEX `idx_user_phone_4e3ecc`(`phone` ASC) USING BTREE,
  INDEX `idx_user_is_acti_83722a`(`is_active` ASC) USING BTREE,
  INDEX `idx_user_is_supe_b8a218`(`is_superuser` ASC) USING BTREE,
  INDEX `idx_user_last_lo_af118a`(`last_login` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_favorites
-- ----------------------------
DROP TABLE IF EXISTS `user_favorites`;
CREATE TABLE `user_favorites`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `target_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '收藏类型(case/template/resource)',
  `target_id` int NOT NULL COMMENT '目标ID',
  `user_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_user_favorites_case_unique`(`user_id` ASC, `target_type` ASC, `target_id` ASC) USING BTREE,
  INDEX `fk_user_fav_user_78d4141d`(`user_id` ASC) USING BTREE,
  INDEX `idx_user_favori_created_dc8e18`(`created_at` ASC) USING BTREE,
  INDEX `idx_user_favori_updated_0347ef`(`updated_at` ASC) USING BTREE,
  INDEX `idx_user_favori_target__97839a`(`target_type` ASC) USING BTREE,
  INDEX `idx_user_favori_target__24a213`(`target_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_fav_user_78d4141d` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户收藏' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_rating
-- ----------------------------
DROP TABLE IF EXISTS `user_rating`;
CREATE TABLE `user_rating`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `target_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '评分类型(case/template)',
  `target_id` int NOT NULL COMMENT '目标ID',
  `rating` double NOT NULL COMMENT '评分(1-5，支持0.5步长)',
  `comment` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '评论',
  `user_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_user_rat_user_689bc080`(`user_id` ASC) USING BTREE,
  INDEX `idx_user_rating_created_c1b3d1`(`created_at` ASC) USING BTREE,
  INDEX `idx_user_rating_updated_70cb31`(`updated_at` ASC) USING BTREE,
  INDEX `idx_user_rating_target__a2cca9`(`target_type` ASC) USING BTREE,
  INDEX `idx_user_rating_target__40e47a`(`target_id` ASC) USING BTREE,
  INDEX `idx_user_rating_rating_b9c77b`(`rating` ASC) USING BTREE,
  CONSTRAINT `fk_user_rat_user_689bc080` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户评分' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_role
-- ----------------------------
DROP TABLE IF EXISTS `user_role`;
CREATE TABLE `user_role`  (
  `user_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  UNIQUE INDEX `uidx_user_role_user_id_d0bad3`(`user_id` ASC, `role_id` ASC) USING BTREE,
  INDEX `role_id`(`role_id` ASC) USING BTREE,
  CONSTRAINT `user_role_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
