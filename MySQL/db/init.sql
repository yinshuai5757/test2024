-- ai DB definition
CREATE DATABASE `ai` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
use `ai`;

-- ai.statuses definition
CREATE TABLE `waiting_statuses` (
  `waiting_status_id` bigint unsigned NOT NULL COMMENT 'id',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '名称',
  `memo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT 'メモ',
  `created_datetime` datetime DEFAULT NULL COMMENT 'レコード作成日時',
  `updated_datetime` datetime DEFAULT NULL COMMENT 'レコード更新日時',
  `deleted_datetime` datetime DEFAULT NULL COMMENT 'レコード削除日時',
  PRIMARY KEY (`waiting_status_id`),
  UNIQUE KEY `waiting_statuses_unique` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ai.ai_types definition
CREATE TABLE `ai_types` (
  `ai_type_id` bigint unsigned NOT NULL COMMENT 'id',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '名称',
  `attention_text` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '注意メッセージ',
  `memo` text COLLATE utf8mb4_unicode_ci COMMENT 'メモ（フロントではしない管理用の情報）',
  `created_datetime` datetime DEFAULT NULL COMMENT 'レコード作成日時',
  `updated_datetime` datetime DEFAULT NULL COMMENT 'レコード更新日時',
  `deleted_datetime` datetime DEFAULT NULL COMMENT 'レコード削除日時',
  PRIMARY KEY (`ai_type_id`),
  UNIQUE KEY `ai_types_unique` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ai.templates definition
CREATE TABLE `templates` (
  `template_id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '名称',
  `template_tree` json DEFAULT NULL COMMENT 'テンプレートの内容',
  `sample_case_memo` text COLLATE utf8mb4_unicode_ci COMMENT 'サンプルケースメモ',
  `created_datetime` datetime DEFAULT NULL COMMENT 'レコード作成日時',
  `updated_datetime` datetime DEFAULT NULL COMMENT 'レコード更新日時',
  `deleted_datetime` datetime DEFAULT NULL COMMENT 'レコード削除日時',
  PRIMARY KEY (`template_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='テンプレート';

-- ai.documents definition
CREATE TABLE `documents` (
  `document_id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `session_user_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'セッションID。バックエンドAPPが振る。',
  `generated_content` json DEFAULT NULL COMMENT 'ユーザによる編集も含めて最終的に生成されたドキュメント全体。（wordファイルexportの段階で保存する）',
  `user_agent` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'UserAgent',
  `created_datetime` datetime DEFAULT NULL COMMENT 'レコード作成日時',
  `updated_datetime` datetime DEFAULT NULL COMMENT 'レコード更新日時',
  PRIMARY KEY (`document_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='生成する文書ごと親データ';

-- ai.document_texts definition
CREATE TABLE `document_texts` (
  `document_text_id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'id',
  `document_id` bigint unsigned NOT NULL COMMENT 'documents.document_id',
  `waiting_status_id` bigint unsigned NOT NULL COMMENT 'waiting_statuses.waiting_status_id',
  `ai_type_id` bigint unsigned NOT NULL COMMENT 'ai_types.ai_type_id',
  `sample_case_memo` text COLLATE utf8mb4_unicode_ci COMMENT 'サンプルケースメモ',
  `sample_format` text COLLATE utf8mb4_unicode_ci COMMENT 'サンプルフォーマット',
  `sample_generated_text` text COLLATE utf8mb4_unicode_ci COMMENT 'サンプル生成分',
  `user_case_memo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT 'ケースメモ（ヒアリング内容）',
  `user_format` text COLLATE utf8mb4_unicode_ci COMMENT 'フォーマット',
  `user_generated_text` text COLLATE utf8mb4_unicode_ci COMMENT '生成された本文',
  `ai_generate_start_datetime` datetime DEFAULT NULL COMMENT 'AI生成開始日時',
  `ai_generate_end_datetime` datetime DEFAULT NULL COMMENT 'AI生成終了日時',
  `created_datetime` datetime DEFAULT NULL COMMENT 'レコード作成日時',
  `updated_datetime` datetime DEFAULT NULL COMMENT 'レコード更新日時',
  PRIMARY KEY (`document_text_id`),
  KEY `document_texts_documents_FK` (`document_id`),
  KEY `document_texts_waiting_statuses_FK` (`waiting_status_id`),
  KEY `document_texts_ai_types_FK` (`ai_type_id`),
  CONSTRAINT `document_texts_ai_types_FK` FOREIGN KEY (`ai_type_id`) REFERENCES `ai_types` (`ai_type_id`),
  CONSTRAINT `document_texts_documents_FK` FOREIGN KEY (`document_id`) REFERENCES `documents` (`document_id`),
  CONSTRAINT `document_texts_waiting_statuses_FK` FOREIGN KEY (`waiting_status_id`) REFERENCES `waiting_statuses` (`waiting_status_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='生成する文書のノードごとの処理用データ';